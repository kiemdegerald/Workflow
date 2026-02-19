/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class WorkflowDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            stats: {},
            recentRequests: [],
            isLoading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            // Récupération des statistiques et données récentes
            const result = await this.orm.call(
                "workflow.request",
                "get_dashboard_data",
                []
            );
            
            this.state.stats = result.stats;
            this.state.recentRequests = result.recent_requests;
            this.state.isLoading = false;
        } catch (error) {
            console.error("Erreur chargement dashboard:", error);
            this.state.isLoading = false;
        }
    }

    formatAmount(amount) {
        if (!amount) return "0";
        return Math.floor(amount).toLocaleString("fr-FR").replace(/,/g, " ");
    }

    openNewRequest() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "workflow.request",
            views: [[false, "form"]],
            target: "current",
        });
    }

    openRequest(requestId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "workflow.request",
            res_id: requestId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

WorkflowDashboard.template = "workflow.Dashboard";

registry.category("actions").add("workflow_dashboard", WorkflowDashboard);
