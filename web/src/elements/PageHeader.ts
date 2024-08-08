import { DEFAULT_CONFIG } from "@goauthentik/common/api/config";
import {
    EVENT_API_DRAWER_TOGGLE,
    EVENT_NOTIFICATION_DRAWER_TOGGLE,
    EVENT_SIDEBAR_TOGGLE,
    EVENT_WS_MESSAGE,
    TITLE_DEFAULT,
} from "@goauthentik/common/constants";
import { currentInterface } from "@goauthentik/common/sentry";
import { me } from "@goauthentik/common/users";
import { AKElement } from "@goauthentik/elements/Base";
import { WithBrandConfig } from "@goauthentik/elements/Interface/brandProvider";
import "@patternfly/elements/pf-tooltip/pf-tooltip.js";

import { msg } from "@lit/localize";
import { CSSResult, TemplateResult, css, html } from "lit";
import { customElement, property } from "lit/decorators.js";

import PFButton from "@patternfly/patternfly/components/Button/button.css";
import PFContent from "@patternfly/patternfly/components/Content/content.css";
import PFPage from "@patternfly/patternfly/components/Page/page.css";
import PFBase from "@patternfly/patternfly/patternfly-base.css";

import { EventsApi } from "@goauthentik/api";

@customElement("ak-page-header")
export class PageHeader extends WithBrandConfig(AKElement) {
    @property()
    icon?: string;

    @property({ type: Boolean })
    iconImage = false;

    @property({ type: Boolean })
    hasNotifications = false;

    @property()
    header = "";

    @property()
    description?: string;

    static get styles(): CSSResult[] {
        return [
            PFBase,
            PFButton,
            PFPage,
            PFContent,
            css`
                .bar {
                    display: flex;
                    flex-direction: row;
                    min-height: 114px;
                }
                .pf-c-button.pf-m-plain {
                    background-color: transparent;
                    border-radius: 0px;
                }
                .pf-c-page__main-section.pf-m-light {
                    background-color: transparent;
                }
                .pf-c-page__main-section {
                    flex-grow: 1;
                    flex-shrink: 1;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }
                img.pf-icon {
                    max-height: 24px;
                }
                .sidebar-trigger,
                .notification-trigger {
                    font-size: 24px;
                }
                .notification-trigger.has-notifications {
                    color: var(--pf-global--active-color--100);
                }
                h1 {
                    display: flex;
                    flex-direction: row;
                    align-items: center !important;
                }
            `,
        ];
    }

    constructor() {
        super();
        window.addEventListener(EVENT_WS_MESSAGE, () => {
            this.firstUpdated();
        });
    }

    firstUpdated(): void {
        me().then((user) => {
            new EventsApi(DEFAULT_CONFIG)
                .eventsNotificationsList({
                    seen: false,
                    ordering: "-created",
                    pageSize: 1,
                    user: user.user.pk,
                })
                .then((r) => {
                    this.hasNotifications = r.pagination.count > 0;
                });
        });
    }

    setTitle(header?: string) {
        const currentIf = currentInterface();
        let title = this.brand?.brandingTitle || TITLE_DEFAULT;
        if (currentIf === "admin") {
            title = `${msg("Admin")} - ${title}`;
        }
        // Prepend the header to the title
        if (header !== undefined && header !== "") {
            title = `${header} - ${title}`;
        }
        document.title = title;
    }

    willUpdate() {
        // Always update title, even if there's no header value set,
        // as in that case we still need to return to the generic title
        this.setTitle(this.header);
    }

    renderIcon(): TemplateResult {
        if (this.icon) {
            if (this.iconImage && !this.icon.startsWith("fa://")) {
                return html`<img class="pf-icon" src="${this.icon}" alt="page icon" />`;
            }
            const icon = this.icon.replaceAll("fa://", "fa ");
            return html`<i class=${icon}></i>`;
        }
        return html``;
    }

    render(): TemplateResult {
        return html`<div class="bar">
            <button
                class="sidebar-trigger pf-c-button pf-m-plain"
                @click=${() => {
                    this.dispatchEvent(
                        new CustomEvent(EVENT_SIDEBAR_TOGGLE, {
                            bubbles: true,
                            composed: true,
                        }),
                    );
                }}
            >
                <i class="fas fa-bars"></i>
            </button>
            <section class="pf-c-page__main-section pf-m-light">
                <div class="pf-c-content">
                    <h1>
                        <slot name="icon">${this.renderIcon()}</slot>&nbsp;
                        <slot name="header">${this.header}</slot>
                    </h1>
                    ${this.description ? html`<p>${this.description}</p>` : html``}
                </div>
            </section>
            <button
                class="notification-trigger pf-c-button pf-m-plain"
                @click=${() => {
                    this.dispatchEvent(
                        new CustomEvent(EVENT_API_DRAWER_TOGGLE, {
                            bubbles: true,
                            composed: true,
                        }),
                    );
                }}
            >
                <pf-tooltip position="top" content=${msg("Open API drawer")}>
                    <i class="fas fa-code"></i>
                </pf-tooltip>
            </button>
            <button
                class="notification-trigger pf-c-button pf-m-plain ${this.hasNotifications
                    ? "has-notifications"
                    : ""}"
                @click=${() => {
                    this.dispatchEvent(
                        new CustomEvent(EVENT_NOTIFICATION_DRAWER_TOGGLE, {
                            bubbles: true,
                            composed: true,
                        }),
                    );
                }}
            >
                <pf-tooltip position="top" content=${msg("Open Notification drawer")}>
                    <i class="fas fa-bell"></i>
                </pf-tooltip>
            </button>
        </div>`;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        "ak-page-header": PageHeader;
    }
}
