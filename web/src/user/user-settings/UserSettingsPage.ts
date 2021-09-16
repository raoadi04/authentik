import { t } from "@lingui/macro";
import { CSSResult, customElement, html, LitElement, property, TemplateResult } from "lit-element";

import PFPage from "@patternfly/patternfly/components/Page/page.css";
import PFContent from "@patternfly/patternfly/components/Content/content.css";
import PFGallery from "@patternfly/patternfly/layouts/Gallery/gallery.css";
import PFCard from "@patternfly/patternfly/components/Card/card.css";
import PFDescriptionList from "@patternfly/patternfly/components/DescriptionList/description-list.css";
import PFSizing from "@patternfly/patternfly/utilities/Sizing/sizing.css";
import PFFlex from "@patternfly/patternfly/utilities/Flex/flex.css";
import PFDisplay from "@patternfly/patternfly/utilities/Display/display.css";
import AKGlobal from "../../authentik.css";
import PFBase from "@patternfly/patternfly/patternfly-base.css";
import PFForm from "@patternfly/patternfly/components/Form/form.css";
import PFFormControl from "@patternfly/patternfly/components/FormControl/form-control.css";
import "../../elements/Tabs";
import "./tokens/UserTokenList";
import "./UserSelfForm";
import "./sources/SourceSettings";
import "./stages/StageSettings";

@customElement("ak-user-settings")
export class UserSettingsPage extends LitElement {
    static get styles(): CSSResult[] {
        return [
            PFBase,
            PFPage,
            PFFlex,
            PFDisplay,
            PFGallery,
            PFContent,
            PFCard,
            PFDescriptionList,
            PFSizing,
            PFForm,
            PFFormControl,
            AKGlobal,
        ];
    }

    render(): TemplateResult {
        return html`<div class="pf-c-page">
            <main role="main" class="pf-c-page__main" tabindex="-1">
                <ak-tabs ?vertical="${true}">
                    <section
                        slot="page-details"
                        data-tab-title="${t`User details`}"
                        class="pf-c-page__main-section pf-m-no-padding-mobile"
                    >
                        <div class="pf-c-card">
                            <div class="pf-c-card__title">${t`Update details`}</div>
                            <div class="pf-c-card__body">
                                <ak-user-self-form .instancePk=${1}></ak-user-self-form>
                            </div>
                        </div>
                    </section>
                    <section
                        slot="page-stages"
                        data-tab-title="${t`Password, 2FA, etc`}"
                        class="pf-c-page__main-section pf-m-no-padding-mobile"
                    >
                        <ak-user-settings-stage></ak-user-settings-stage>
                    </section>
                    <section
                        slot="page-sources"
                        data-tab-title="${t`Connected services`}"
                        class="pf-c-page__main-section pf-m-no-padding-mobile"
                    >
                        <ak-user-settings-source></ak-user-settings-source>
                    </section>
                    <section
                        slot="page-tokens"
                        data-tab-title="${t`Tokens and App passwords`}"
                        class="pf-c-page__main-section pf-m-no-padding-mobile"
                    >
                        <ak-user-token-list></ak-user-token-list>
                    </section>
                </ak-tabs>
            </main>
        </div>`;
    }
}
