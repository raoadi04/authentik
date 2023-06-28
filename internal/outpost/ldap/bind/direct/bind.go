package direct

import (
	"context"

	"github.com/getsentry/sentry-go"
	"github.com/nmcclain/ldap"
	"github.com/prometheus/client_golang/prometheus"
	log "github.com/sirupsen/logrus"
	"goauthentik.io/internal/outpost/flow"
	"goauthentik.io/internal/outpost/ldap/bind"
	"goauthentik.io/internal/outpost/ldap/flags"
	"goauthentik.io/internal/outpost/ldap/metrics"
)

func (db *DirectBinder) Bind(username string, req *bind.Request) (ldap.LDAPResultCode, error) {
	fe := flow.NewFlowExecutor(req.Context(), db.si.GetAuthenticationFlowSlug(), db.si.GetAPIClient().GetConfig(), log.Fields{
		"bindDN":    req.BindDN,
		"client":    req.RemoteAddr(),
		"requestId": req.ID(),
	})
	fe.DelegateClientIP(req.RemoteAddr())
	fe.Params.Add("goauthentik.io/outpost/ldap", "true")

	fe.Answers[flow.StageIdentification] = username
	fe.Answers[flow.StagePassword] = req.BindPW

	passed, err := fe.Execute()
	flags := flags.UserFlags{
		Session: fe.GetSession(),
		UserPk:  -1,
	}
	//only set, if empty
	if db.si.GetFlags(req.BindDN) == nil {
		db.si.SetFlags(req.BindDN, &flags)
	}
	if err != nil {
		metrics.RequestsRejected.With(prometheus.Labels{
			"outpost_name": db.si.GetOutpostName(),
			"type":         "bind",
			"reason":       "flow_error",
			"app":          db.si.GetAppSlug(),
		}).Inc()
		req.Log().WithError(err).Warning("failed to execute flow")
		return ldap.LDAPResultInvalidCredentials, nil
	}
	if !passed {
		metrics.RequestsRejected.With(prometheus.Labels{
			"outpost_name": db.si.GetOutpostName(),
			"type":         "bind",
			"reason":       "invalid_credentials",
			"app":          db.si.GetAppSlug(),
		}).Inc()
		req.Log().Info("Invalid credentials")
		return ldap.LDAPResultInvalidCredentials, nil
	}

	access, err := fe.CheckApplicationAccess(db.si.GetAppSlug())
	if !access {
		req.Log().Info("Access denied for user")
		metrics.RequestsRejected.With(prometheus.Labels{
			"outpost_name": db.si.GetOutpostName(),
			"type":         "bind",
			"reason":       "access_denied",
			"app":          db.si.GetAppSlug(),
		}).Inc()
		return ldap.LDAPResultInsufficientAccessRights, nil
	}
	if err != nil {
		metrics.RequestsRejected.With(prometheus.Labels{
			"outpost_name": db.si.GetOutpostName(),
			"type":         "bind",
			"reason":       "access_check_fail",
			"app":          db.si.GetAppSlug(),
		}).Inc()
		req.Log().WithError(err).Warning("failed to check access")
		return ldap.LDAPResultOperationsError, nil
	}
	req.Log().Info("User has access")
	uisp := sentry.StartSpan(req.Context(), "authentik.providers.ldap.bind.user_info")
	// Get user info to store in context
	userInfo, _, err := fe.ApiClient().CoreApi.CoreUsersMeRetrieve(context.Background()).Execute()
	if err != nil {
		metrics.RequestsRejected.With(prometheus.Labels{
			"outpost_name": db.si.GetOutpostName(),
			"type":         "bind",
			"reason":       "user_info_fail",
			"app":          db.si.GetAppSlug(),
		}).Inc()
		req.Log().WithError(err).Warning("failed to get user info")
		return ldap.LDAPResultOperationsError, nil
	}
	cs := db.SearchAccessCheck(userInfo.User)
	flags.UserPk = userInfo.User.Pk
	flags.CanSearch = cs != nil
	db.si.SetFlags(req.BindDN, &flags)
	if flags.CanSearch {
		req.Log().WithField("group", cs).Info("Allowed access to search")
	}
	uisp.Finish()
	return ldap.LDAPResultSuccess, nil
}
