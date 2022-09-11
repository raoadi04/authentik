import "@goauthentik/web/admin/stages/prompt/PromptForm";
import { DEFAULT_CONFIG } from "@goauthentik/web/common/api/config";
import { uiConfig } from "@goauthentik/web/common/ui/config";
import { truncate } from "@goauthentik/web/common/utils";
import "@goauthentik/web/elements/buttons/ModalButton";
import "@goauthentik/web/elements/buttons/SpinnerButton";
import "@goauthentik/web/elements/forms/DeleteBulkForm";
import "@goauthentik/web/elements/forms/ModalForm";
import { PaginatedResponse } from "@goauthentik/web/elements/table/Table";
import { TableColumn } from "@goauthentik/web/elements/table/Table";
import { TablePage } from "@goauthentik/web/elements/table/TablePage";

import { t } from "@lingui/macro";

import { TemplateResult, html } from "lit";
import { customElement, property } from "lit/decorators.js";

import { Prompt, StagesApi } from "@goauthentik/api";

@customElement("ak-stage-prompt-list")
export class PromptListPage extends TablePage<Prompt> {
    searchEnabled(): boolean {
        return true;
    }
    pageTitle(): string {
        return t`Prompts`;
    }
    pageDescription(): string {
        return t`Single Prompts that can be used for Prompt Stages.`;
    }
    pageIcon(): string {
        return "pf-icon pf-icon-plugged";
    }

    checkbox = true;

    @property()
    order = "order";

    async apiEndpoint(page: number): Promise<PaginatedResponse<Prompt>> {
        return new StagesApi(DEFAULT_CONFIG).stagesPromptPromptsList({
            ordering: this.order,
            page: page,
            pageSize: (await uiConfig()).pagination.perPage,
            search: this.search || "",
        });
    }

    columns(): TableColumn[] {
        return [
            new TableColumn(t`Field`, "field_key"),
            new TableColumn(t`Label`, "label"),
            new TableColumn(t`Type`, "type"),
            new TableColumn(t`Order`, "order"),
            new TableColumn(t`Stages`),
            new TableColumn(t`Actions`),
        ];
    }

    renderToolbarSelected(): TemplateResult {
        const disabled = this.selectedElements.length < 1;
        return html`<ak-forms-delete-bulk
            objectLabel=${t`Prompt(s)`}
            .objects=${this.selectedElements}
            .usedBy=${(item: Prompt) => {
                return new StagesApi(DEFAULT_CONFIG).stagesPromptPromptsUsedByList({
                    promptUuid: item.pk,
                });
            }}
            .delete=${(item: Prompt) => {
                return new StagesApi(DEFAULT_CONFIG).stagesPromptPromptsDestroy({
                    promptUuid: item.pk,
                });
            }}
        >
            <button ?disabled=${disabled} slot="trigger" class="pf-c-button pf-m-danger">
                ${t`Delete`}
            </button>
        </ak-forms-delete-bulk>`;
    }

    row(item: Prompt): TemplateResult[] {
        return [
            html`${item.fieldKey}`,
            html`${truncate(item.label, 20)}`,
            html`${item.type}`,
            html`${item.order}`,
            html`${item.promptstageSet?.map((stage) => {
                return html`<li>${stage.name}</li>`;
            })}`,
            html` <ak-forms-modal>
                <span slot="submit"> ${t`Update`} </span>
                <span slot="header"> ${t`Update Prompt`} </span>
                <ak-prompt-form slot="form" .instancePk=${item.pk}> </ak-prompt-form>
                <button slot="trigger" class="pf-c-button pf-m-plain">
                    <i class="fas fa-edit"></i>
                </button>
            </ak-forms-modal>`,
        ];
    }

    renderObjectCreate(): TemplateResult {
        return html`
            <ak-forms-modal>
                <span slot="submit"> ${t`Create`} </span>
                <span slot="header"> ${t`Create Prompt`} </span>
                <ak-prompt-form slot="form"> </ak-prompt-form>
                <button slot="trigger" class="pf-c-button pf-m-primary">${t`Create`}</button>
            </ak-forms-modal>
        `;
    }
}
