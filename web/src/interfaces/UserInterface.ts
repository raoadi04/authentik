import "../elements/messages/MessageContainer";
import {
    css,
    CSSResult,
    customElement,
    html,
    LitElement,
    property,
    TemplateResult,
} from "lit-element";
import { me } from "../api/Users";
import "./locale";
import "../elements/sidebar/SidebarItem";
import { t } from "@lingui/macro";
import PFBase from "@patternfly/patternfly/patternfly-base.css";
import PFPage from "@patternfly/patternfly/components/Page/page.css";
import PFBrand from "@patternfly/patternfly/components/Brand/brand.css";
import PFButton from "@patternfly/patternfly/components/Button/button.css";
import PFDrawer from "@patternfly/patternfly/components/Drawer/drawer.css";
import PFAvatar from "@patternfly/patternfly/components/Avatar/avatar.css";
import PFDropdown from "@patternfly/patternfly/components/Dropdown/dropdown.css";
import AKGlobal from "../authentik.css";

import "../elements/buttons/Dropdown";
import "../elements/router/RouterOutlet";
import "../elements/messages/MessageContainer";
import "../elements/notifications/NotificationDrawer";
import "../elements/sidebar/Sidebar";
import { EVENT_API_DRAWER_TOGGLE, EVENT_NOTIFICATION_DRAWER_TOGGLE } from "../constants";
import { CurrentTenant, EventsApi } from "@goauthentik/api";
import { DEFAULT_CONFIG, tenant } from "../api/Config";
import { WebsocketClient } from "../common/ws";
import { ROUTES } from "../routesUser";
import { first } from "../utils";
import { DefaultTenant } from "../elements/sidebar/SidebarBrand";
import { until } from "lit-html/directives/until";

export const UIConfig = {
    enabledFeatures: {
        apiDrawer: true,
        notificationDrawer: true,
        settings: true,
    },
};

@customElement("ak-interface-user")
export class UserInterface extends LitElement {
    @property({ type: Boolean })
    notificationOpen = false;

    @property({ type: Boolean })
    apiDrawerOpen = false;

    ws: WebsocketClient;

    @property({ attribute: false })
    tenant: CurrentTenant = DefaultTenant;

    @property({ type: Boolean })
    hasNotifications = false;

    static get styles(): CSSResult[] {
        return [
            PFBase,
            PFBrand,
            PFPage,
            PFAvatar,
            PFButton,
            PFDrawer,
            PFDropdown,
            AKGlobal,
            css`
                .pf-c-page__main,
                .pf-c-drawer__content,
                .pf-c-page__drawer {
                    z-index: auto !important;
                }
                .display-none {
                    display: none;
                }
                .pf-c-brand {
                    min-height: 48px;
                }
                .has-notifications {
                    color: #2b9af3;
                }
            `,
        ];
    }

    constructor() {
        super();
        this.ws = new WebsocketClient();
        window.addEventListener(EVENT_NOTIFICATION_DRAWER_TOGGLE, () => {
            this.notificationOpen = !this.notificationOpen;
        });
        window.addEventListener(EVENT_API_DRAWER_TOGGLE, () => {
            this.apiDrawerOpen = !this.apiDrawerOpen;
        });
        tenant().then((tenant) => (this.tenant = tenant));
        new EventsApi(DEFAULT_CONFIG)
            .eventsNotificationsList({
                seen: false,
                ordering: "-created",
                pageSize: 1,
            })
            .then((r) => {
                this.hasNotifications = r.pagination.count > 0;
            });
    }

    render(): TemplateResult {
        return html` <div class="pf-c-page">
            <header class="pf-c-page__header">
                <div class="pf-c-page__header-brand">
                    <a href="#/" class="pf-c-page__header-brand-link">
                        <img
                            class="pf-c-brand"
                            src="${first(this.tenant.brandingLogo, DefaultTenant.brandingLogo)}"
                            alt="${(this.tenant.brandingTitle, DefaultTenant.brandingTitle)}"
                        />
                    </a>
                </div>
                <div class="pf-c-page__header-tools">
                    <div class="pf-c-page__header-tools-group">
                        ${UIConfig.enabledFeatures.apiDrawer ?
                        html`<div
                            class="pf-c-page__header-tools-item pf-m-hidden pf-m-visible-on-lg"
                        >
                            <button
                                class="pf-c-button pf-m-plain"
                                type="button"
                                @click=${() => {
                                    this.apiDrawerOpen = !this.apiDrawerOpen;
                                }}
                            >
                                <i class="fas fa-code" aria-hidden="true"></i>
                            </button>
                        </div>`:html``}
                        ${UIConfig.enabledFeatures.notificationDrawer ? html`
                        <div class="pf-c-page__header-tools-item pf-m-hidden pf-m-visible-on-lg">
                            <button
                                class="pf-c-button pf-m-plain ${this.hasNotifications
                                    ? "has-notifications"
                                    : ""}"
                                type="button"
                                @click=${() => {
                                    this.notificationOpen = !this.notificationOpen;
                                }}
                            >
                                <i class="fas fa-bell" aria-hidden="true"></i>
                            </button>
                        </div>`:html``}
                    </div>
                    <div class="pf-c-page__header-tools-group">
                        <div class="pf-c-page__header-tools-item pf-m-hidden pf-m-visible-on-md">
                            <ak-dropdown class="pf-c-dropdown">
                                <button class="pf-m-plain pf-c-dropdown__toggle" type="button">
                                    <span class="pf-c-dropdown__toggle-text"
                                        >${until(
                                            me().then((me) => {
                                                return me.user.username;
                                            }),
                                        )}</span
                                    >
                                    <span class="pf-c-dropdown__toggle-icon">
                                        <i class="fas fa-caret-down" aria-hidden="true"></i>
                                    </span>
                                </button>
                                <ul class="pf-c-dropdown__menu" hidden>
                                    ${UIConfig.enabledFeatures.settings ? html`
                                    <li>
                                        <a class="pf-c-dropdown__menu-item" href="#/user">
                                            ${t`Settings`}
                                        </a>
                                    </li>
                                    ` : html``}
                                    <li>
                                        <a class="pf-c-dropdown__menu-item" href="/flows/-/default/invalidation/">
                                            ${t`Sign out`}
                                        </a>
                                    </li>
                                </ul>
                            </ak-dropdown>
                        </div>
                    </div>
                    ${until(
                        me().then((me) => {
                            return html`<img
                                class="pf-c-avatar"
                                src=${me.user.avatar}
                                alt="${t`Avatar image`}"
                            />`;
                        }),
                    )}
                </div>
            </header>
            <div class="pf-c-page__drawer">
                <div
                    class="pf-c-drawer ${this.notificationOpen || this.apiDrawerOpen
                        ? "pf-m-expanded"
                        : "pf-m-collapsed"}"
                >
                    <div class="pf-c-drawer__main">
                        <div class="pf-c-drawer__content">
                            <div class="pf-c-drawer__body">
                                <main class="pf-c-page__main">
                                    <ak-router-outlet
                                        role="main"
                                        class="pf-l-bullseye__item pf-c-page__main"
                                        tabindex="-1"
                                        id="main-content"
                                        defaultUrl="/library"
                                        .routes=${ROUTES}
                                    >
                                    </ak-router-outlet>
                                </main>
                            </div>
                        </div>
                        <ak-notification-drawer
                            class="pf-c-drawer__panel pf-m-width-33 ${this.notificationOpen
                                ? ""
                                : "display-none"}"
                            ?hidden=${!this.notificationOpen}
                        ></ak-notification-drawer>
                        <ak-api-drawer
                            class="pf-c-drawer__panel pf-m-width-33 ${this.apiDrawerOpen
                                ? ""
                                : "display-none"}"
                            ?hidden=${!this.apiDrawerOpen}
                        ></ak-api-drawer>
                    </div>
                </div>
            </div>
        </div>`;
    }
}
