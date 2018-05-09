$(document).ready(function(){
    $(".public-key").click(function(){
        $("#key-body").text($(this).attr("key-body"));
        $("#key-modal").modal('show');
    });

    $('[data-toggle="popover"]').popover({
        html: true,
        placement: 'auto right',
        container: 'body'
    });

    try {
        $('table.datatable').dataTable({
            'searching': false,
            'paging': false,
            'info': false
        });
    } catch(e) {
        console.log("error in datatable init: ", e);
    }

    $("#createModal").on("shown.bs.modal", function(){
        $("#tagname").focus();
    });

    $("#revokeModal").on("show.bs.modal", function(e) {
        var button = $(e.relatedTarget);
        var mappingId = button.data("mapping-id");

        var modal = $(e.currentTarget);

        var form = modal.find(".revoke-permission-form")
        form.attr("action", "/groups/{{group.name}}/service/{{user.username}}/revoke/" + mappingId);
    });

    $("#removeUserModal").on("show.bs.modal", function(e) {
        var button = $(e.relatedTarget);
        var memberName = button.data("member-name");
        var memberType = button.data("member-type");

        var modal = $(e.currentTarget);
        modal.find(".member-name").html(memberName);

        var form = modal.find(".remove-member-form");
        form.attr("action", "/groups/{{ group.id }}/remove");
        form.find("input[name=member]").val(memberName);
        form.find("input[name=member_type]").val(memberType);
    });

    $("select#member").attr("data-placeholder", "Select a user or group").chosen();

    $('#add-form-expiration').datetimepicker({
        pickTime: false,
        icons: {
            time: "fa fa-clock-o",
            date: "fa fa-calendar",
            up: "fa fa-arrow-up",
            down: "fa fa-arrow-down"
        },
        useCurrent: false,
        minDate: moment(),
    });

    $('#join-form-expiration').datetimepicker({
        pickTime: false,
        icons: {
            time: "fa fa-clock-o",
            date: "fa fa-calendar",
            up: "fa fa-arrow-up",
            down: "fa fa-arrow-down"
        },
        useCurrent: false,
        minDate: moment(),
    });

    $('#edit-form-expiration').datetimepicker({
        pickTime: false,
        icons: {
            time: "fa fa-clock-o",
            date: "fa fa-calendar",
            up: "fa fa-arrow-up",
            down: "fa fa-arrow-down"
        },
        useCurrent: false,
        minDate: moment(),
    });

    $('#audit-form-ends-at').datetimepicker({
        pickTime: false,
        icons: {
            time: "fa fa-clock-o",
            date: "fa fa-calendar",
            up: "fa fa-arrow-up",
            down: "fa fa-arrow-down"
        },
        useCurrent: false,
        minDate: moment(),
    });

    $("#formSubmit").click(function() {
        $("#createFrom").submit();
    });

    var auditModel = $('#auditModal');

    if (auditModel &&
        auditModel.data('group-auditing') === 'True' &&
        auditModel.data('group-owner') === 'True') {

        auditModel.modal('show');
    }
});
