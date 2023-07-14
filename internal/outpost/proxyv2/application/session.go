package application

import (
	"math"
	"net/url"
	"os"
	"path"
	"strings"

	"github.com/gorilla/securecookie"
	"github.com/gorilla/sessions"
	"goauthentik.io/api/v3"
	"goauthentik.io/internal/config"
	"goauthentik.io/internal/outpost/proxyv2/codecs"
	"goauthentik.io/internal/outpost/proxyv2/constants"
	"goauthentik.io/internal/outpost/proxyv2/redisstore"
)

const RedisKeyPrefix = "authentik_proxy_session_"
// Amount of time for cookies/redis keys to expire.
const sessionExpire = 86400 * 30

func (a *Application) getStore(p api.ProxyOutpostConfig, externalHost *url.URL) sessions.Store {
	maxAge := 0
	if p.AccessTokenValidity.IsSet() {
		t := p.AccessTokenValidity.Get()
		// Add one to the validity to ensure we don't have a session with indefinite length
		maxAge = int(*t) + 1
	}

	redisURL, err := url.Parse(config.Get().Redis.URL)

	if err != nil {
		client, err := redisstore.GetRedisClient(redisURL)
		if err != nil {
			panic(err)
		}
		rs, err := redisstore.NewStoreWithUniversalClient(
			client,
			redisstore.WithOptions(&sessions.Options{
				Path: "/",
				Domain: *p.CookieDomain,
				MaxAge: sessionExpire,
			}),
			redisstore.WithKeyPrefix(RedisKeyPrefix),
			redisstore.WithMaxLength(math.MaxInt),
			redisstore.WithCodecs(codecs.CodecsFromPairs(maxAge, []byte(*p.CookieSecret))),
		)
		if err != nil {
			panic(err)
		}

		a.log.Trace("using redis session backend")
		return rs
	}
	dir := os.TempDir()
	cs := sessions.NewFilesystemStore(dir)
	cs.Codecs = codecs.CodecsFromPairs(maxAge, []byte(*p.CookieSecret))
	// https://github.com/markbates/goth/commit/7276be0fdf719ddff753f3574ef0f967e4a5a5f7
	// set the maxLength of the cookies stored on the disk to a larger number to prevent issues with:
	// securecookie: the value is too long
	// when using OpenID Connect , since this can contain a large amount of extra information in the id_token

	// Note, when using the FilesystemStore only the session.ID is written to a browser cookie, so this is explicit for the storage on disk
	cs.MaxLength(math.MaxInt)
	cs.Options.Domain = *p.CookieDomain
	a.log.WithField("dir", dir).Trace("using filesystem session backend")
	return cs
}

func (a *Application) SessionName() string {
	return a.sessionName
}

func (a *Application) getAllCodecs() []securecookie.Codec {
	apps := a.srv.Apps()
	cs := []securecookie.Codec{}
	for _, app := range apps {
		cs = append(cs, codecs.CodecsFromPairs(0, []byte(*app.proxyConfig.CookieSecret))...)
	}
	return cs
}

func (a *Application) Logout(sub string) error {
	if _, ok := a.sessions.(*sessions.FilesystemStore); ok {
		files, err := os.ReadDir(os.TempDir())
		if err != nil {
			return err
		}
		for _, file := range files {
			s := sessions.Session{}
			if !strings.HasPrefix(file.Name(), "session_") {
				continue
			}
			fullPath := path.Join(os.TempDir(), file.Name())
			data, err := os.ReadFile(fullPath)
			if err != nil {
				a.log.WithError(err).Warning("failed to read file")
				continue
			}
			err = securecookie.DecodeMulti(
				a.SessionName(), string(data),
				&s.Values, a.getAllCodecs()...,
			)
			if err != nil {
				a.log.WithError(err).Trace("failed to decode session")
				continue
			}
			rc, ok := s.Values[constants.SessionClaims]
			if !ok || rc == nil {
				continue
			}
			claims := s.Values[constants.SessionClaims].(Claims)
			if claims.Sub == sub {
				a.log.WithField("path", fullPath).Trace("deleting session")
				err := os.Remove(fullPath)
				if err != nil {
					a.log.WithError(err).Warning("failed to delete session")
					continue
				}
			}
		}
	}
	if rs, ok := a.sessions.(*redisstore.RedisStore); ok {
		keys, err := rs.Keys()
		if err != nil {
			return err
		}
		for _, key := range keys {
			b, err := rs.GetBytesByKey(key)
			if err != nil {
				a.log.WithError(err).Warning("failed to load value")
				continue
			}
			s := sessions.Session{}
			err = rs.Deserialize(b, &s)
			if err != nil {
				a.log.WithError(err).Warning("failed to deserialize")
				continue
			}
			c := s.Values[constants.SessionClaims]
			if c == nil {
				continue
			}
			claims := c.(Claims)
			if claims.Sub == sub {
				a.log.WithField("key", key).Trace("deleting session")
				err := rs.DeleteByKey(key)
				if err != nil {
					a.log.WithError(err).Warning("failed to delete key")
					continue
				}
			}
		}
	}
	return nil
}
