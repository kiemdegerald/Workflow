/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

/**
 * Service d'application du thème bancaire clair
 * Force l'application du design professionnel
 */
export const workflowThemeService = {
    dependencies: [],
    
    start() {
        // Injecter le CSS directement dans le DOM
        const style = document.createElement('style');
        style.id = 'workflow-theme-forced';
        style.textContent = `
            /* THÈME BANCAIRE PROFESSIONNEL - INJECTION FORCÉE */
            
            /* Bouton Nouveau (Create) */
            body .o_control_panel .o_cp_buttons .btn-primary,
            body .o_form_button_create {
                background: #0A4B78 !important;
                border-color: #0A4B78 !important;
                color: white !important;
                font-weight: 600 !important;
                border-radius: 8px !important;
                padding: 0.5rem 1.5rem !important;
                transition: all 0.2s !important;
            }
            
            body .o_control_panel .o_cp_buttons .btn-primary:hover,
            body .o_form_button_create:hover {
                background: #083A5E !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(10, 75, 120, 0.3) !important;
            }
            
            /* Vue Liste - Container */
            body .o_list_view {
                background: white !important;
                border-radius: 12px !important;
                border: 1px solid #E2E8F0 !important;
                overflow: hidden !important;
            }
            
            /* En-tête du tableau */
            body .o_list_view thead {
                background: #F3F4F6 !important;
            }
            
            body .o_list_view thead th {
                color: #4B5563 !important;
                font-weight: 700 !important;
                font-size: 12px !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
                padding: 1rem 1.25rem !important;
                border-bottom: 2px solid #E2E8F0 !important;
            }
            
            /* Lignes du tableau */
            body .o_list_view tbody tr {
                border-bottom: 1px solid #E2E8F0 !important;
                transition: background-color 0.15s ease !important;
            }
            
            body .o_list_view tbody tr:hover {
                background: #F9FAFB !important;
            }
            
            body .o_list_view tbody td {
                padding: 1rem 1.25rem !important;
                font-size: 14px !important;
                color: #374151 !important;
            }
            
            /* Badges de statut */
            body .badge {
                padding: 0.375rem 0.75rem !important;
                border-radius: 6px !important;
                font-size: 12px !important;
                font-weight: 600 !important;
            }
            
            /* Statut Brouillon */
            body .badge.text-muted {
                background: rgba(107, 114, 128, 0.1) !important;
                color: #6B7280 !important;
            }
            
            /* Statut Soumis */
            body .badge.text-info {
                background: rgba(59, 130, 246, 0.1) !important;
                color: #3B82F6 !important;
            }
            
            /* Statut En cours */
            body .badge.text-warning {
                background: rgba(232, 149, 58, 0.1) !important;
                color: #E8953A !important;
            }
            
            /* Statut Approuvé */
            body .badge.text-success {
                background: rgba(22, 163, 74, 0.1) !important;
                color: #16A34A !important;
            }
            
            /* Statut Refusé */
            body .badge.text-danger {
                background: rgba(220, 38, 38, 0.1) !important;
                color: #DC2626 !important;
            }
            
            /* Fond des lignes colorées */
            body .o_list_view tbody tr.text-info {
                background: rgba(59, 130, 246, 0.02) !important;
            }
            
            body .o_list_view tbody tr.text-warning {
                background: rgba(232, 149, 58, 0.02) !important;
            }
            
            body .o_list_view tbody tr.text-success {
                background: rgba(22, 163, 74, 0.02) !important;
            }
            
            body .o_list_view tbody tr.text-danger {
                background: rgba(220, 38, 38, 0.02) !important;
            }
            
            /* Panel de contrôle */
            body .o_control_panel {
                background: white !important;
                border-bottom: 1px solid #E2E8F0 !important;
            }
            
            /* Barre de recherche */
            body .o_searchview {
                background: white !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 8px !important;
            }
            
            body .o_searchview input {
                border: none !important;
                padding: 0.5rem !important;
            }
            
            body .o_searchview .o_searchview_facet {
                background: #0A4B78 !important;
                color: white !important;
                border-radius: 6px !important;
                padding: 0.25rem 0.75rem !important;
            }
            
            /* Formulaires */
            body .o_form_view .o_form_sheet_bg {
                background: #F8FAFC !important;
            }
            
            body .o_form_view .o_form_sheet {
                background: white !important;
                border-radius: 12px !important;
                border: 1px solid #E2E8F0 !important;
                padding: 2rem !important;
            }
            
            /* Champs de formulaire */
            body .o_field_widget input,
            body .o_field_widget select,
            body .o_field_widget textarea {
                border: 1px solid #E2E8F0 !important;
                border-radius: 8px !important;
                padding: 0.625rem !important;
                transition: all 0.2s !important;
            }
            
            body .o_field_widget input:focus,
            body .o_field_widget select:focus,
            body .o_field_widget textarea:focus {
                border-color: #0A4B78 !important;
                box-shadow: 0 0 0 3px rgba(10, 75, 120, 0.1) !important;
            }
            
            /* Labels */
            body .o_form_label {
                color: #374151 !important;
                font-weight: 600 !important;
                font-size: 13px !important;
            }
            
            /* Content background */
            body .o_content {
                background: #F8FAFC !important;
            }
            
            /* Boutons secondaires */
            body .btn-secondary {
                background: white !important;
                border: 1px solid #E2E8F0 !important;
                color: #374151 !important;
                font-weight: 600 !important;
                border-radius: 8px !important;
            }
            
            body .btn-secondary:hover {
                background: #F3F4F6 !important;
            }
            
            /* Animation */
            body .o_content {
                animation: workflowFadeIn 0.3s ease !important;
            }
            
            @keyframes workflowFadeIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        
        // Ajouter le style au head
        if (!document.getElementById('workflow-theme-forced')) {
            document.head.appendChild(style);
        }
        
        console.log('✅ Workflow Theme: Thème bancaire professionnel appliqué');
        
        return {};
    },
};

registry.category("services").add("workflowTheme", workflowThemeService);
