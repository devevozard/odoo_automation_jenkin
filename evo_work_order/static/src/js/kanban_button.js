odoo.define('evo_work_order.kanban_button', function(require) {
    "use strict";
    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var viewRegistry = require('web.view_registry');

    var KanbanButton = KanbanController.include({
        buttons_template: 'button_near_create.button',

        events: _.extend({}, KanbanController.prototype.events, {
            'click .custom_method_button': '_callCustomMethod',
        }),
        
        _callCustomMethod: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var self = this;
            var record = this.model.get(this.handle);
            if (!record) {
                return;
            }
            var recordID = record.res_id;
            this._rpc({
                model: 'workorder.report',
                method: 'action_update',  
                args: [[recordID]], 
            }).then(function() {
    
                self.trigger_up('reload');
            }).catch(function(error) {
            });
        },
    });
    
    var WorkOrderKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: KanbanButton
        }),
    });

    viewRegistry.add('button_in_kanban', WorkOrderKanbanView);
});
