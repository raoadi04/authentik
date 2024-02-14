import { AndNext, DEFAULT_CONFIG } from "@goauthentik/common/api/config";
import { deviceTypeName } from "@goauthentik/common/labels";
import "@goauthentik/elements/buttons/Dropdown";
import "@goauthentik/elements/buttons/ModalButton";
import "@goauthentik/elements/buttons/TokenCopyButton";
import "@goauthentik/elements/forms/DeleteBulkForm";
import "@goauthentik/elements/forms/ModalForm";
import { PaginatedResponse, Table, TableColumn } from "@goauthentik/elements/table/Table";
import "@goauthentik/user/user-settings/mfa/MFADeviceForm";
import "@patternfly/elements/pf-tooltip/pf-tooltip.js";

import { msg } from "@lit/localize";
import { TemplateResult, html } from "lit";
import { customElement, property } from "lit/decorators.js";
import { ifDefined } from "lit/directives/if-defined.js";

import { AuthenticatorsApi, Device, UserSetting } from "@goauthentik/api";

export const stageToAuthenticatorName = (stage: UserSetting) =>
    stage.title ?? `Invalid stage component ${stage.component}`;

@customElement("ak-user-settings-mfa")
export class MFADevicesPage extends Table<Device> {
    @property({ attribute: false })
    userSettings?: UserSetting[];

    checkbox = true;
    clearOnRefresh = true;

    async apiEndpoint(): Promise<PaginatedResponse<Device>> {
        const devices = await new AuthenticatorsApi(DEFAULT_CONFIG).authenticatorsAllList();
        return {
            pagination: {
                current: 0,
                count: devices.length,
                totalPages: 1,
                startIndex: 1,
                endIndex: devices.length,
                next: 0,
                previous: 0,
            },
            results: devices,
        };
    }

    columns(): TableColumn[] {
        // prettier-ignore
        return [
            msg("Name"),
            msg("Type"),
            ""
        ].map((th) => new TableColumn(th, ""));
    }

    renderToolbar(): TemplateResult {
        const settings = (this.userSettings || []).filter((stage) => {
            if (stage.component === "ak-user-settings-password") {
                return false;
            }
            return stage.configureUrl;
        });
        return html`<ak-dropdown class="pf-c-dropdown">
                <button class="pf-m-primary pf-c-dropdown__toggle" type="button">
                    <span class="pf-c-dropdown__toggle-text">${msg("Enroll")}</span>
                    <i class="fas fa-caret-down pf-c-dropdown__toggle-icon" aria-hidden="true"></i>
                </button>
                <ul class="pf-c-dropdown__menu" hidden>
                    ${settings.map((stage) => {
                        return html`<li>
                            <a
                                href="${ifDefined(stage.configureUrl)}${AndNext(
                                    `/if/user/#/settings;${JSON.stringify({
                                        page: "page-mfa",
                                    })}`,
                                )}"
                                class="pf-c-dropdown__menu-item"
                            >
                                ${stageToAuthenticatorName(stage)}
                            </a>
                        </li>`;
                    })}
                </ul>
            </ak-dropdown>
            ${super.renderToolbar()}`;
    }

    async deleteWrapper(device: Device) {
        const api = new AuthenticatorsApi(DEFAULT_CONFIG);
        switch (device.type.toLowerCase()) {
            case "authentik_stages_authenticator_duo.duodevice":
                return api.authenticatorsDuoDestroy({ id: parseInt(device.pk, 10) });
            case "authentik_stages_authenticator_sms.smsdevice":
                return api.authenticatorsSmsDestroy({ id: parseInt(device.pk, 10) });
            case "authentik_stages_authenticator_totp.totpdevice":
                return api.authenticatorsTotpDestroy({ id: parseInt(device.pk, 10) });
            case "authentik_stages_authenticator_static.staticdevice":
                return api.authenticatorsStaticDestroy({ id: parseInt(device.pk, 10) });
            case "authentik_stages_authenticator_webauthn.webauthndevice":
                return api.authenticatorsWebauthnDestroy({ id: parseInt(device.pk, 10) });
            case "authentik_stages_authenticator_mobile.mobiledevice":
                return api.authenticatorsMobileDestroy({
                    uuid: device.pk,
                });
            default:
                break;
        }
    }

    renderToolbarSelected(): TemplateResult {
        const disabled = this.selectedElements.length < 1;
        return html`<ak-forms-delete-bulk
            objectLabel=${msg("Device(s)")}
            .objects=${this.selectedElements}
            .delete=${(item: Device) => {
                return this.deleteWrapper(item);
            }}
        >
            <button ?disabled=${disabled} slot="trigger" class="pf-c-button pf-m-danger">
                ${msg("Delete")}
            </button>
        </ak-forms-delete-bulk>`;
    }

    row(item: Device): TemplateResult[] {
        return [
            html`${item.name}`,
            html`${deviceTypeName(item)}`,
            html`
                <ak-forms-modal>
                    <span slot="submit">${msg("Update")}</span>
                    <span slot="header">${msg("Update Device")}</span>
                    <ak-user-mfa-form slot="form" deviceType=${item.type} .instancePk=${item.pk}>
                    </ak-user-mfa-form>
                    <button slot="trigger" class="pf-c-button pf-m-plain">
                        <pf-tooltip position="top" content=${msg("Edit")}>
                            <i class="fas fa-edit"></i>
                        </pf-tooltip>
                    </button>
                </ak-forms-modal>
            `,
        ];
    }
}
