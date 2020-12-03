package server

import (
	"crypto/sha512"
	"encoding/hex"
	"fmt"
	"math/rand"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"

	"github.com/BeryJu/authentik/proxy/pkg"
	"github.com/BeryJu/authentik/proxy/pkg/client"
	"github.com/BeryJu/authentik/proxy/pkg/client/outposts"
	"github.com/getsentry/sentry-go"
	"github.com/go-openapi/runtime"
	"github.com/recws-org/recws"

	httptransport "github.com/go-openapi/runtime/client"
	"github.com/go-openapi/strfmt"
	"github.com/oauth2-proxy/oauth2-proxy/pkg/apis/options"
	log "github.com/sirupsen/logrus"
)

const ConfigLogLevel = "log_level"
const ConfigErrorReportingEnabled = "error_reporting_enabled"
const ConfigErrorReportingEnvironment = "error_reporting_environment"

// APIController main controller which connects to the authentik api via http and ws
type APIController struct {
	client *client.Authentik
	auth   runtime.ClientAuthInfoWriter
	token  string

	server *Server

	commonOpts *options.Options

	lastBundleHash string
	logger         *log.Entry

	reloadOffset time.Duration

	wsConn *recws.RecConn
}

func getCommonOptions() *options.Options {
	commonOpts := options.NewOptions()
	commonOpts.Cookie.Name = "authentik_proxy"
	commonOpts.EmailDomains = []string{"*"}
	commonOpts.ProviderType = "oidc"
	commonOpts.ProxyPrefix = "/akprox"
	commonOpts.Logging.SilencePing = true
	commonOpts.SetAuthorization = false
	commonOpts.Scope = "openid email profile ak_proxy"
	return commonOpts
}

func doGlobalSetup(config map[string]interface{}) {
	switch config[ConfigLogLevel].(string) {
	case "debug":
		log.SetLevel(log.DebugLevel)
	case "info":
		log.SetLevel(log.InfoLevel)
	case "warning":
		log.SetLevel(log.WarnLevel)
	case "error":
		log.SetLevel(log.ErrorLevel)
	default:
		log.SetLevel(log.DebugLevel)
	}
	log.WithField("version", pkg.VERSION).Info("Starting authentik proxy")

	var dsn string
	if config[ConfigErrorReportingEnabled].(bool) {
		dsn = "https://a579bb09306d4f8b8d8847c052d3a1d3@sentry.beryju.org/8"
		log.Debug("Error reporting enabled")
	}

	err := sentry.Init(sentry.ClientOptions{
		Dsn:         dsn,
		Environment: config[ConfigErrorReportingEnvironment].(string),
	})
	if err != nil {
		log.Fatalf("sentry.Init: %s", err)
	}

	defer sentry.Flush(2 * time.Second)
}

func getTLSTransport() http.RoundTripper {
	value, set := os.LookupEnv("AUTHENTIK_INSECURE")
	if !set {
		value = "false"
	}
	tlsTransport, err := httptransport.TLSTransport(httptransport.TLSClientOptions{
		InsecureSkipVerify: strings.ToLower(value) == "true",
	})
	if err != nil {
		panic(err)
	}
	return tlsTransport
}

// NewAPIController initialise new API Controller instance from URL and API token
func NewAPIController(pbURL url.URL, token string) *APIController {
	transport := httptransport.New(pbURL.Host, client.DefaultBasePath, []string{pbURL.Scheme})
	transport.Transport = SetUserAgent(getTLSTransport(), fmt.Sprintf("authentik-proxy@%s", pkg.VERSION))

	// create the transport
	auth := httptransport.BasicAuth("", token)

	// create the API client, with the transport
	apiClient := client.New(transport, strfmt.Default)

	// Because we don't know the outpost UUID, we simply do a list and pick the first
	// The service account this token belongs to should only have access to a single outpost
	outposts, err := apiClient.Outposts.OutpostsOutpostsList(outposts.NewOutpostsOutpostsListParams(), auth)

	if err != nil {
		panic(err)
	}
	outpost := outposts.Payload.Results[0]
	doGlobalSetup(outpost.Config.(map[string]interface{}))

	ac := &APIController{
		client: apiClient,
		auth:   auth,
		token:  token,

		logger:     log.WithField("component", "api-controller"),
		commonOpts: getCommonOptions(),
		server:     NewServer(),

		reloadOffset: time.Duration(rand.Intn(10)) * time.Second,

		lastBundleHash: "",
	}
	ac.logger.Debugf("HA Reload offset: %s", ac.reloadOffset)
	ac.initWS(pbURL, outpost.Pk)
	return ac
}

func (a *APIController) bundleProviders() ([]*providerBundle, error) {
	providers, err := a.client.Outposts.OutpostsProxyList(outposts.NewOutpostsProxyListParams(), a.auth)
	if err != nil {
		a.logger.WithError(err).Error("Failed to fetch providers")
		return nil, err
	}
	// Check provider hash to see if anything is changed
	hasher := sha512.New()
	bin, _ := providers.Payload.MarshalBinary()
	hash := hex.EncodeToString(hasher.Sum(bin))
	if hash == a.lastBundleHash {
		return nil, nil
	}
	a.lastBundleHash = hash

	bundles := make([]*providerBundle, len(providers.Payload.Results))

	for idx, provider := range providers.Payload.Results {
		externalHost, err := url.Parse(*provider.ExternalHost)
		if err != nil {
			log.WithError(err).Warning("Failed to parse URL, skipping provider")
		}
		bundles[idx] = &providerBundle{
			a:    a,
			Host: externalHost.Host,
		}
		bundles[idx].Build(provider)
	}
	return bundles, nil
}

func (a *APIController) updateHTTPServer(bundles []*providerBundle) {
	newMap := make(map[string]*providerBundle)
	for _, bundle := range bundles {
		newMap[bundle.Host] = bundle
	}
	a.logger.Debug("Swapped maps")
	a.server.Handlers = newMap
}

// UpdateIfRequired Updates the HTTP Server config if required, automatically swaps the handlers
func (a *APIController) UpdateIfRequired() error {
	bundles, err := a.bundleProviders()
	if err != nil {
		return err
	}
	if bundles == nil {
		a.logger.Debug("Providers have not changed, not updating")
		return nil
	}
	a.updateHTTPServer(bundles)
	return nil
}

// Start Starts all handlers, non-blocking
func (a *APIController) Start() error {
	err := a.UpdateIfRequired()
	if err != nil {
		return err
	}
	go func() {
		a.logger.Debug("Starting HTTP Server...")
		a.server.ServeHTTP()
	}()
	go func() {
		a.logger.Debug("Starting HTTPs Server...")
		a.server.ServeHTTPS()
	}()
	go func() {
		a.logger.Debug("Starting WS Handler...")
		a.startWSHandler()
	}()
	go func() {
		a.logger.Debug("Starting WS Health notifier...")
		a.startWSHealth()
	}()
	return nil
}
