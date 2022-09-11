import "@goauthentik/web/admin/groups/GroupForm";
import "@goauthentik/web/admin/users/RelatedUserList";
import { DEFAULT_CONFIG } from "@goauthentik/web/common/api/config";
import { EVENT_REFRESH } from "@goauthentik/web/common/constants";
import "@goauthentik/web/elements/CodeMirror";
import { PFColor } from "@goauthentik/web/elements/Label";
import "@goauthentik/web/elements/PageHeader";
import "@goauthentik/web/elements/Tabs";
import "@goauthentik/web/elements/buttons/ActionButton";
import "@goauthentik/web/elements/buttons/SpinnerButton";
import "@goauthentik/web/elements/events/ObjectChangelog";
import "@goauthentik/web/elements/forms/ModalForm";

import { t } from "@lingui/macro";

import { CSSResult, LitElement, TemplateResult, html } from "lit";
import { customElement, property } from "lit/decorators.js";

import AKGlobal from "@goauthentik/web/common/styles/authentik.css";
import PFButton from "@patternfly/patternfly/components/Button/button.css";
import PFCard from "@patternfly/patternfly/components/Card/card.css";
import PFContent from "@patternfly/patternfly/components/Content/content.css";
import PFDescriptionList from "@patternfly/patternfly/components/DescriptionList/description-list.css";
import PFPage from "@patternfly/patternfly/components/Page/page.css";
import PFGrid from "@patternfly/patternfly/layouts/Grid/grid.css";
import PFBase from "@patternfly/patternfly/patternfly-base.css";
import PFDisplay from "@patternfly/patternfly/utilities/Display/display.css";
import PFFlex from "@patternfly/patternfly/utilities/Flex/flex.css";
import PFSizing from "@patternfly/patternfly/utilities/Sizing/sizing.css";

import { CoreApi, Group } from "@goauthentik/api";

@customElement("ak-group-view")
export class GroupViewPage extends LitElement {
    @property({ type: String })
    set groupId(id: string) {
        new CoreApi(DEFAULT_CONFIG)
            .coreGroupsRetrieve({
                groupUuid: id,
            })
            .then((group) => {
                this.group = group;
            });
    }

    @property({ attribute: false })
    group?: Group;

    static get styles(): CSSResult[] {
        return [
            PFBase,
            PFPage,
            PFFlex,
            PFButton,
            PFDisplay,
            PFGrid,
            PFContent,
            PFCard,
            PFDescriptionList,
            PFSizing,
            AKGlobal,
        ];
    }

    constructor() {
        super();
        this.addEventListener(EVENT_REFRESH, () => {
            if (!this.group?.pk) return;
            this.groupId = this.group?.pk;
        });
    }

    render(): TemplateResult {
        return html`<ak-page-header
                icon="pf-icon pf-icon-users"
                header=${t`Group ${this.group?.name || ""}`}
                description=${this.group?.name || ""}
            >
            </ak-page-header>
            ${this.renderBody()}`;
    }

    renderBody(): TemplateResult {
        if (!this.group) {
            return html``;
        }
        return html`<ak-tabs>
            <section
                slot="page-overview"
                data-tab-title="${t`Overview`}"
                class="pf-c-page__main-section pf-m-no-padding-mobile"
            >
                <div class="pf-l-grid pf-m-gutter">
                    <div
                        class="pf-c-card pf-l-grid__item pf-m-12-col pf-m-3-col-on-xl pf-m-3-col-on-2xl"
                    >
                        <div class="pf-c-card__title">${t`Group Info`}</div>
                        <div class="pf-c-card__body">
                            <dl class="pf-c-description-list pf-m-2-col">
                                <div class="pf-c-description-list__group">
                                    <dt class="pf-c-description-list__term">
                                        <span class="pf-c-description-list__text">${t`Name`}</span>
                                    </dt>
                                    <dd class="pf-c-description-list__description">
                                        <div class="pf-c-description-list__text">
                                            ${this.group.name}
                                        </div>
                                    </dd>
                                </div>
                                <div class="pf-c-description-list__group">
                                    <dt class="pf-c-description-list__term">
                                        <span class="pf-c-description-list__text"
                                            >${t`Superuser`}</span
                                        >
                                    </dt>
                                    <dd class="pf-c-description-list__description">
                                        <div class="pf-c-description-list__text">
                                            <ak-label
                                                color=${this.group.isSuperuser
                                                    ? PFColor.Green
                                                    : PFColor.Orange}
                                            ></ak-label>
                                        </div>
                                    </dd>
                                </div>
                            </dl>
                        </div>
                        <div class="pf-c-card__footer">
                            <ak-forms-modal>
                                <span slot="submit"> ${t`Update`} </span>
                                <span slot="header"> ${t`Update Group`} </span>
                                <ak-group-form slot="form" .instancePk=${this.group.pk}>
                                </ak-group-form>
                                <button slot="trigger" class="pf-m-primary pf-c-button">
                                    ${t`Edit`}
                                </button>
                            </ak-forms-modal>
                        </div>
                    </div>
                    <div
                        class="pf-c-card pf-l-grid__item pf-m-12-col pf-m-12-col-on-xl pf-m-12-col-on-2xl"
                    >
                        <div class="pf-c-card__title">${t`Changelog`}</div>
                        <div class="pf-c-card__body">
                            <ak-object-changelog
                                targetModelPk=${this.group.pk}
                                targetModelApp="authentik_core"
                                targetModelName="group"
                            >
                            </ak-object-changelog>
                        </div>
                    </div>
                </div>
            </section>
            <section
                slot="page-users"
                data-tab-title="${t`Users`}"
                class="pf-c-page__main-section pf-m-no-padding-mobile"
            >
                <div class="pf-c-card">
                    <div class="pf-c-card__body">
                        <ak-user-related-list groupUuid=${this.group.pk}> </ak-user-related-list>
                    </div>
                </div>
            </section>
        </ak-tabs>`;
    }
}
