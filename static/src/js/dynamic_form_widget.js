/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

/**
 * Widget OWL pour afficher les champs personnalisés d'un workflow
 * directement dans le formulaire (sans popup / sans tree).
 *
 * Usage XML :
 *   <field name="custom_value_ids" widget="workflow_dynamic_form" nolabel="1"/>
 */
export class DynamicFormWidget extends Component {
    static template = "workflow.DynamicFormWidget";
    static props = { ...standardFieldProps };

    // ── Accesseurs ──────────────────────────────────────────────────────────────────────────────────────────────────────

    get lines() {
        // Accès direct : record.data[fieldName] retourne la StaticList one2many
        const staticList = this.props.record.data[this.props.name];
        return staticList?.records || [];
    }

    _valueField(fieldType) {
        return {
            char:     "value_char",
            text:     "value_text",
            integer:  "value_integer",
            float:    "value_float",
            boolean:  "value_boolean",
            date:     "value_date",
            datetime: "value_datetime",
            selection:"value_selection",
        }[fieldType] || "value_char";
    }

    getValue(line) {
        return line.data[this._valueField(line.data.field_type)];
    }

    getSelectionOptions(line) {
        const raw = line.data.selection_options || "";
        return raw.split("\n").map(s => s.trim()).filter(Boolean);
    }

    // ── Handlers ────────────────────────────────────────────────────

    async onFieldChange(line, event) {
        const ft = line.data.field_type;
        const fieldName = this._valueField(ft);
        let value = event.target.value;

        if (ft === "boolean")  value = event.target.checked;
        else if (ft === "integer") value = parseInt(value) || 0;
        else if (ft === "float")   value = parseFloat(value) || 0.0;

        await line.update({ [fieldName]: value });
    }
}

registry.category("fields").add("workflow_dynamic_form", {
    component: DynamicFormWidget,
    supportedTypes: ["one2many"],
});
