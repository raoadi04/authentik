import "@goauthentik/admin/groups/GroupForm";
import { DEFAULT_CONFIG } from "@goauthentik/common/api/config";
import { uiConfig } from "@goauthentik/common/ui/config";
import { PFColor } from "@goauthentik/elements/Label";
import "@goauthentik/elements/buttons/SpinnerButton";
import "@goauthentik/elements/forms/DeleteBulkForm";
import "@goauthentik/elements/forms/ModalForm";
import { PaginatedResponse } from "@goauthentik/elements/table/Table";
import { Table, TableColumn } from "@goauthentik/elements/table/Table";

import { t } from "@lingui/macro";

import { TemplateResult, html } from "lit";
import { customElement, property } from "lit/decorators.js";

import { CoreApi, Group } from "@goauthentik/api";

@customElement("ak-group-related-list")
export class RelatedGroupList extends Table<Group> {
    checkbox = true;
    searchEnabled(): boolean {
        return true;
    }

    @property()
    order = "name";

    @property({ type: Number })
    targetUser?: number;

    async apiEndpoint(page: number): Promise<PaginatedResponse<Group>> {
        return new CoreApi(DEFAULT_CONFIG).coreGroupsList({
            ordering: this.order,
            page: page,
            pageSize: (await uiConfig()).pagination.perPage,
            search: this.search || "",
            membersByPk: this.targetUser ? [this.targetUser] : [],
        });
    }

    columns(): TableColumn[] {
        return [
            new TableColumn(t`Name`, "name"),
            new TableColumn(t`Parent`, "parent"),
            new TableColumn(t`Superuser privileges?`),
            new TableColumn(t`Actions`),
        ];
    }

    renderToolbarSelected(): TemplateResult {
        const disabled = this.selectedElements.length < 1;
        return html`<ak-forms-delete-bulk
            objectLabel=${t`Group(s)`}
            .objects=${this.selectedElements}
            .usedBy=${(item: Group) => {
                return new CoreApi(DEFAULT_CONFIG).coreGroupsUsedByList({
                    groupUuid: item.pk,
                });
            }}
            .delete=${(item: Group) => {
                return new CoreApi(DEFAULT_CONFIG).coreGroupsDestroy({
                    groupUuid: item.pk,
                });
            }}
        >
            <button ?disabled=${disabled} slot="trigger" class="pf-c-button pf-m-danger">
                ${t`Delete`}
            </button>
        </ak-forms-delete-bulk>`;
    }

    row(item: Group): TemplateResult[] {
        return [
            html`<a href="#/identity/groups/${item.pk}">${item.name}</a>`,
            html`${item.parentName || t`-`}`,
            html`<ak-label color=${item.isSuperuser ? PFColor.Green : PFColor.Grey}>
                ${item.isSuperuser ? t`Yes` : t`No`}
            </ak-label>`,
            html` <ak-forms-modal>
                <span slot="submit"> ${t`Update`} </span>
                <span slot="header"> ${t`Update Group`} </span>
                <ak-group-form slot="form" .instancePk=${item.pk}> </ak-group-form>
                <button slot="trigger" class="pf-c-button pf-m-plain">
                    <i class="fas fa-edit"></i>
                </button>
            </ak-forms-modal>`,
        ];
    }
}
