import { $, browser } from "@wdio/globals";

browser.addCommand(
    "focus",
    function () {
        browser.execute(function (domElement) {
            domElement.focus();
            // @ts-ignore
        }, this);
    },
    true,
);

export class AkSearchSelectViewDriver {
    constructor(
        public element: WebdriverIO.Element,
        public menu: WebdriverIO.Element,
    ) {
        /* no op */
    }

    static async build(element: WebdriverIO.Element) {
        const tagname = await element.getTagName();
        const comptype = await element.getAttribute("data-ouia-component-type");
        if (comptype !== "ak-search-select-view") {
            throw new Error(
                `SearchSelectView driver passed incorrect component. Expected ak-search-select-view, got ${comptype ? `'${comptype}` : `No test data type, tag name: '${tagname}'`}`,
            );
        }
        const id = await element.getAttribute("data-ouia-component-id");
        const menu = await $(`[data-ouia-component-id="menu-${id}"]`);
        return new AkSearchSelectViewDriver(element, menu);
    }

    get open() {
        return this.element.getProperty("open");
    }

    async input() {
        return await this.element.$(">>>input");
    }

    async listElements() {
        return await this.menu.$$(">>>li");
    }

    async focusOnInput() {
        // @ts-ignore
        await (await this.input()).focus();
    }

    async inputIsVisible() {
        return await this.element.$(">>>input").isDisplayed();
    }

    async menuIsVisible() {
        return (await this.menu.isExisting()) && (await this.menu.isDisplayed());
    }

    async clickInput() {
        return await (await this.input()).click();
    }
}
