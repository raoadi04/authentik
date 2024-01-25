import "@goauthentik/app/admin/roles/RolePermissionGlobalTable";
import "@goauthentik/app/admin/roles/RolePermissionObjectTable";
import "@goauthentik/app/admin/users/UserAssignedGlobalPermissionsTable";
import "@goauthentik/app/admin/users/UserAssignedObjectPermissionsTable";
import { AKElement } from "@goauthentik/app/elements/Base";
import "@goauthentik/app/elements/rbac/RoleObjectPermissionTable";
import "@goauthentik/app/elements/rbac/UserObjectPermissionTable";
import "@goauthentik/elements/Tabs";

import { msg } from "@lit/localize";
import { CSSResult, TemplateResult, html } from "lit";
import { customElement, property } from "lit/decorators.js";

import PFBanner from "@patternfly/patternfly/components/Banner/banner.css";
import PFCard from "@patternfly/patternfly/components/Card/card.css";
import PFPage from "@patternfly/patternfly/components/Page/page.css";
import PFGrid from "@patternfly/patternfly/layouts/Grid/grid.css";
import PFBase from "@patternfly/patternfly/patternfly-base.css";

import { RbacPermissionsAssignedByUsersListModelEnum } from "@goauthentik/api";

@customElement("ak-rbac-object-permission-page")
export class ObjectPermissionPage extends AKElement {
    @property()
    model?: RbacPermissionsAssignedByUsersListModelEnum;

    @property()
    objectPk?: string | number;

    @property({ type: Boolean })
    embedded = false;

    static get styles(): CSSResult[] {
        return [PFBase, PFGrid, PFPage, PFCard, PFBanner];
    }

    render(): TemplateResult {
        return html`${!this.embedded
                ? html`<div class="pf-c-banner pf-m-info">
                      ${msg("RBAC is in preview.")}
                      <a href="mailto:hello@goauthentik.io">${msg("Send us feedback!")}</a>
                  </div>`
                : html``}
            <ak-tabs pageIdentifier="permissionPage" ?vertical=${!this.embedded}>
                ${this.model === RbacPermissionsAssignedByUsersListModelEnum.CoreUser
                    ? html`
                          <div
                              slot="page-assigned-permissions"
                              data-tab-title="${msg("Assigned permissions")}"
                              class=""
                          >
                              <section class="pf-c-page__main-section pf-m-no-padding-mobile">
                                  <div class="pf-l-grid pf-m-gutter">
                                      <div class="pf-c-card pf-l-grid__item pf-m-12-col">
                                          <div class="pf-c-card__title">
                                              ${msg("Assigned global permissions")}
                                          </div>
                                          <div class="pf-c-card__body">
                                              <ak-user-assigned-global-permissions-table
                                                  userId=${this.objectPk as number}
                                              >
                                              </ak-user-assigned-global-permissions-table>
                                          </div>
                                      </div>
                                      <div class="pf-c-card pf-l-grid__item pf-m-12-col">
                                          <div class="pf-c-card__title">
                                              ${msg("Assigned object permissions")}
                                          </div>
                                          <div class="pf-c-card__body">
                                              <ak-user-assigned-object-permissions-table
                                                  userId=${this.objectPk as number}
                                              >
                                              </ak-user-assigned-object-permissions-table>
                                          </div>
                                      </div>
                                  </div>
                              </section>
                          </div>
                      `
                    : html``}
                ${this.model === RbacPermissionsAssignedByUsersListModelEnum.RbacRole
                    ? html`
                          <div
                              slot="page-assigned-permissions"
                              data-tab-title="${msg("Assigned permissions")}"
                              class=""
                          >
                              <section class="pf-c-page__main-section pf-m-no-padding-mobile">
                                  <div class="pf-l-grid pf-m-gutter">
                                      <div class="pf-c-card pf-l-grid__item pf-m-12-col">
                                          <div class="pf-c-card__title">
                                              ${msg("Assigned global permissions")}
                                          </div>
                                          <div class="pf-c-card__body">
                                              <ak-role-permissions-global-table
                                                  userId=${this.objectPk as string}
                                              >
                                              </ak-role-permissions-global-table>
                                          </div>
                                      </div>
                                      <div class="pf-c-card pf-l-grid__item pf-m-12-col">
                                          <div class="pf-c-card__title">
                                              ${msg("Assigned object permissions")}
                                          </div>
                                          <div class="pf-c-card__body">
                                              <ak-role-permissions-object-table
                                                  userId=${this.objectPk as string}
                                              >
                                              </ak-role-permissions-object-table>
                                          </div>
                                      </div>
                                  </div>
                              </section>
                          </div>
                      `
                    : html``}
                <section
                    slot="page-object-user"
                    data-tab-title="${msg("User Object Permissions")}"
                    class="pf-c-page__main-section pf-m-no-padding-mobile"
                >
                    <div class="pf-l-grid pf-m-gutter">
                        <div class="pf-c-card pf-l-grid__item pf-m-12-col">
                            <div class="pf-c-card__title">${msg("User Object Permissions")}</div>
                            <div class="pf-c-card__body">
                                <ak-rbac-user-object-permission-table
                                    .model=${this.model}
                                    .objectPk=${this.objectPk}
                                >
                                </ak-rbac-user-object-permission-table>
                            </div>
                        </div>
                    </div>
                </section>
                <section
                    slot="page-object-role"
                    data-tab-title="${msg("Role Object Permissions")}"
                    class="pf-c-page__main-section pf-m-no-padding-mobile"
                >
                    <div class="pf-l-grid pf-m-gutter">
                        <div class="pf-c-card pf-l-grid__item pf-m-12-col">
                            <div class="pf-c-card__title">${msg("Role Object Permissions")}</div>
                            <div class="pf-c-card__body">
                                <ak-rbac-role-object-permission-table
                                    .model=${this.model}
                                    .objectPk=${this.objectPk}
                                >
                                </ak-rbac-role-object-permission-table>
                            </div>
                        </div>
                    </div>
                </section>
            </ak-tabs>`;
    }
}
