import { AKElement } from "@goauthentik/elements/Base";

import { CSSResult, TemplateResult, css, html } from "lit";
import { customElement } from "lit/decorators.js";

import PFBase from "@patternfly/patternfly/patternfly-base.css";

/**
 * @class Divider
 * @element ak-divider
 *
 * Divider is a horizontal rule, an in-page element to separate displayed items.
 *
 * @slot - HTML to display in-line in the middle of the horizontal rule.
 */
@customElement("ak-divider")
export class Divider extends AKElement {
    static get styles(): CSSResult[] {
        return [
            PFBase,
            css`
                .separator {
                    display: flex;
                    align-items: center;
                    text-align: center;
                }

                .separator::before,
                .separator::after {
                    content: "";
                    flex: 1;
                    border-bottom: 1px solid var(--pf-global--Color--100);
                }

                .separator:not(:empty)::before {
                    margin-right: 0.25em;
                }

                .separator:not(:empty)::after {
                    margin-left: 0.25em;
                }
            `,
        ];
    }

    render(): TemplateResult {
        return html`<div class="separator"><slot></slot></div>`;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        "ak-divider": Divider;
    }
}
