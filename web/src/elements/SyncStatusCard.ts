import { EVENT_REFRESH } from "@goauthentik/authentik/common/constants";
import { AKElement } from "@goauthentik/authentik/elements/Base";
import "@goauthentik/elements/events/LogViewer";
import "@goauthentik/elements/EmptyState";

import { msg, str } from "@lit/localize";
import { CSSResult, TemplateResult, html, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import "@goauthentik/components/ak-status-label";

import PFCard from "@patternfly/patternfly/components/Card/card.css";
import PFBase from "@patternfly/patternfly/patternfly-base.css";

import { SyncStatus, SystemTask, SystemTaskStatusEnum } from "@goauthentik/api";
import { getRelativeTime } from "@goauthentik/authentik/common/utils";

@customElement("ak-sync-status-card")
export class SyncStatusCard extends AKElement {
    @state()
    syncState?: SyncStatus;

    @state()
    loading = false;

    @property({ attribute: false })
    fetch!: () => Promise<SyncStatus>;

    @property({ attribute: false })
    triggerSync!: () => Promise<unknown>;

    static get styles(): CSSResult[] {
        return [PFBase, PFCard];
    }

    firstUpdated() {
        this.loading = true;
        this.fetch().then((status) => {
            this.syncState = status;
            this.loading = false;
        });
    }

    renderSyncTask(task: SystemTask): TemplateResult {
        return html`<li>
            ${(this.syncState?.tasks || []).length > 1 ? html`<span>${task.name}</span>` : nothing}
            <span><ak-status-label ?good=${task.status === SystemTaskStatusEnum.Successful} good-label=${msg("Finished successfully")} bad-label=${msg("Finished with errors")}></ak-status-label></span>
            <span>${msg(str`Finished ${getRelativeTime(task.finishTimestamp)} (${task.finishTimestamp.toLocaleString()})`)}</span>
            <ak-log-viewer .logs=${task?.messages}></ak-log-viewer>
        </li> `;
    }

    renderSyncStatus(): TemplateResult {
        if (this.loading) {
            return html`<ak-empty-state ?loading=${true}></ak-empty-state>`;
        }
        if (!this.syncState) {
            return html`${msg("No sync status.")}`;
        }
        if (this.syncState.isRunning) {
            return html`${msg("Sync currently running.")}`;
        }
        if (this.syncState.tasks.length < 1) {
            return html`${msg("Not synced yet.")}`;
        }
        return html`
            <ul class="pf-c-list">
                ${this.syncState.tasks.map((task) => {
                    return this.renderSyncTask(task);
                })}
            </ul>
        `;
    }

    render(): TemplateResult {
        return html`<div class="pf-c-card">
            <div class="pf-c-card__title">${msg("Sync status")}</div>
            <div class="pf-c-card__body">${this.renderSyncStatus()}</div>
            <div class="pf-c-card__footer">
                <ak-action-button
                    class="pf-m-secondary"
                    ?disabled=${this.syncState?.isRunning}
                    .apiRequest=${() => {
                        if (this.syncState) {
                            // This is a bit of a UX cheat, we set isRunning to true to disable the button
                            // and change the text even before we hear back from the backend
                            this.syncState = {
                                ...this.syncState,
                                isRunning: true,
                            };
                        }
                        this.triggerSync().then(() => {
                            this.dispatchEvent(
                                new CustomEvent(EVENT_REFRESH, {
                                    bubbles: true,
                                    composed: true,
                                }),
                            );
                            this.firstUpdated();
                        });
                    }}
                >
                    ${this.syncState?.isRunning
                        ? msg("Sync currently running")
                        : msg("Run sync again")}
                </ak-action-button>
            </div>
        </div>`;
    }
}