import { customElement } from "lit-element";
import { CoreApi } from "authentik-api";
import { DEFAULT_CONFIG } from "../../../api/Config";
import { AKChart } from "../../../elements/charts/Chart";
import { t } from "@lingui/macro";
import { ChartOptions, ChartData } from "chart.js";

interface UserMetrics {
    count: number;
    superusers: number;
}

@customElement("ak-admin-status-chart-user-count")
export class UserCountStatusChart extends AKChart<UserMetrics> {
    getChartType(): string {
        return "doughnut";
    }

    getOptions(): ChartOptions {
        return {
            plugins: {
                legend: {
                    display: false,
                },
            },
            maintainAspectRatio: false,
        };
    }

    async apiRequest(): Promise<UserMetrics> {
        const api = new CoreApi(DEFAULT_CONFIG);
        const count = (
            await api.coreUsersList({
                pageSize: 1,
            })
        ).pagination.count;
        const superusers = (
            await api.coreUsersList({
                isSuperuser: true,
            })
        ).pagination.count;
        this.centerText = count.toString();
        return {
            count: count - superusers,
            superusers,
        };
    }

    getChartData(data: UserMetrics): ChartData {
        return {
            labels: [t`Total users`, t`Superusers`],
            datasets: [
                {
                    backgroundColor: ["#2b9af3", "#3e8635"],
                    spanGaps: true,
                    data: [data.count, data.superusers],
                },
            ],
        };
    }
}
