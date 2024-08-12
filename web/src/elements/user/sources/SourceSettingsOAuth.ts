import { AndNext, DEFAULT_CONFIG } from "@goauthentik/common/api/config.js";
import { EVENT_REFRESH } from "@goauthentik/common/constants.js";
import { MessageLevel } from "@goauthentik/common/messages.js";
import "@goauthentik/elements/Spinner";
import { showMessage } from "@goauthentik/elements/messages/MessageContainer";
import { BaseUserSettings } from "@goauthentik/elements/user/sources/BaseUserSettings";

import { msg, str } from "@lit/localize";
import { TemplateResult, html } from "lit";
import { customElement, property } from "lit/decorators.js";

import { SourcesApi } from "@goauthentik/api";

@customElement("ak-user-settings-source-oauth")
export class SourceSettingsOAuth extends BaseUserSettings {
    @property()
    title!: string;

    @property({ type: Number })
    connectionPk = 0;

    render(): TemplateResult {
        if (this.connectionPk === -1) {
            return html`<ak-spinner></ak-spinner>`;
        }
        if (this.connectionPk > 0) {
            return html`<button
                class="pf-c-button pf-m-danger"
                @click=${() => {
                    return new SourcesApi(DEFAULT_CONFIG)
                        .sourcesUserConnectionsOauthDestroy({
                            id: this.connectionPk,
                        })
                        .then(() => {
                            showMessage({
                                level: MessageLevel.info,
                                message: msg("Successfully disconnected source"),
                            });
                        })
                        .catch((exc) => {
                            showMessage({
                                level: MessageLevel.error,
                                message: msg(str`Failed to disconnected source: ${exc}`),
                            });
                        })
                        .finally(() => {
                            this.parentElement?.dispatchEvent(
                                new CustomEvent(EVENT_REFRESH, {
                                    bubbles: true,
                                    composed: true,
                                }),
                            );
                        });
                }}
            >
                ${msg("Disconnect")}
            </button>`;
        }
        if (this.configureUrl) {
            return html`<a
                class="pf-c-button pf-m-primary"
                href="${this.configureUrl}${AndNext(
                    `/if/user/#/settings;${JSON.stringify({ page: "page-sources" })}`,
                )}"
            >
                ${msg("Connect")}
            </a>`;
        }
        return html`${msg("-")}`;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        "ak-user-settings-source-oauth": SourceSettingsOAuth;
    }
}
