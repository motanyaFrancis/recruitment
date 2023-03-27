    $(document).ready(function () {
        var documentID = '{{response.No}}';
        var Process_Type = '{{response.Process_Type}}';
        const $respondModalBtn = $('#respondModalBtn');
        const $attachmentForm = $('#attachmentsForm');
        const $attachment_spinner = $('#attachment_spinner');
        const $attachmentBtn = $('#attachmentBtn');
        const $bid_collapse = $('#bid_collapse');
        const $itemsTable = $('#itemsTable');
        const $bidding_row = $('#bidding_row');
        const $bid_closing = $('#bid_closing');
        const $securityForm = $('#securityForm');
        const $security_spinner = $('#security_spinner');
        const $submitForm = $('#submitForm');
        const $submit_spinner = $('#submit_spinner');

        var tenderSubmitted = false;
        if (!$.fn.DataTable.isDataTable('#line_table')) {
            $('#line_table').DataTable({
                "pageLength": 5,
                "order": [
                    [0, "desc"]
                ]
            });
        }

        function isFloat(str) {
            return !isNaN(parseFloat(str));
        }
        $bid_collapse.click(function () {
            $itemsTable.toggle(1000);
            $bidding_row.toggle(1500);
            $bid_collapse.hide();
        })
        $bid_closing.click(function () {
            $bidding_row.toggle(1000);
            $itemsTable.toggle(1200);
            $bid_collapse.show(1500);
        })

        SecurityData(documentID);


        $securityForm.on("submit", (e) => {
            e.preventDefault();
            if ($('#securityInstitution').val() === '' || $('#securityAmount').val() === '') {
                alert('Please fill in all required fields.');
                return false;
            }
            var securityAmount = $('#securityAmount').val();

            if (isFloat(securityAmount) != true) {
                alert('Security Amount has to be a number');
                return false;
            }
            $security_spinner.show();
            $.ajax({
                url: "/FnCreateProspectiveSupplier/",
                type: "POST",
                data: {
                    Process_Type: $('#Process_Type').val(),
                    docNo: $('#docNo').val(),
                    securityInstitution: $('#securityInstitution').val(),
                    securityAmount: securityAmount,
                    myAction: $('#myAction').val(),
                    TenderType: $('#TenderType').val(),
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function (data) {
                    $('#securityInstitution, #securityAmount').val('');
                    $security_spinner.hide();
                    if (data['success'] == true) {
                        iziToast.show({
                            theme: 'dark',
                            backgroundColor: '#239B56',
                            icon: 'las la-check-circle',
                            title: 'Yeah',
                            message: data['message'],
                            position: 'topRight',
                            progressBarColor: '#F4F6F7',
                        });
                        $('.securityStep').addClass('completed');
                        SecurityData(documentID);
                    } else {
                        iziToast.show({
                            theme: 'dark',
                            icon: 'las la-exclamation',
                            title: 'Error',
                            message: data['error'],
                            position: 'topRight',
                            progressBarColor: '#ff0800',
                        });
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    console.log(xhr.responseText);
                }
            });

        });

        function SecurityData(pk) {
            $.ajax({
                url: "/FnCreateProspectiveSupplier/",
                type: "GET",
                data: {
                    tenderNo: pk,
                },
                dataType: "json",
                success: function (data) {
                    if (data['success'] == true) {
                        $('#myAction').val('modify');
                        $('#securityInstitution').val(data['response'][
                            'Tender_Security_Institution'
                        ]);
                        $('#securityAmount').val(data['response']['Tender_Security_Amount']);
                        $('#nextOne').show();
                        $('.securityStep').addClass('completed');

                        if (data['response']['Response_Submitted'] == false) {
                            $('#submitSecurity').text('Update');
                            $('#submitSecurity .icon i').removeClass('fa-paper-plane');
                            $('#submitSecurity .icon i').addClass('fas fa-edit');
                        } else {
                            $('#submitSecurity').hide();
                            $('#securityAmount').prop('disabled', true);
                            $('#securityInstitution').prop('disabled', true);
                            tenderSubmitted = true;
                            $('#submitForm').hide();
                            $('.completeStep').addClass('completed');
                            $('#submit_first').empty().append('View')
                        }

                    } else {
                        console.log(data['response'])
                    }
                },
                error: function (xhr, status, error) {
                    console.log("Error:", error);
                },
            });
        }

        $('#nextOne').click(function () {
            $('#step1').hide(500);
            $('#step2').show(800);
            FinancialData(documentID);
        })

        FinancialData(documentID);

        function FinancialData(pk) {
            $.ajax({
                url: "/FinancialBid/" + pk + "/",
                type: "GET",
                dataType: "json",
                success: function (data) {
                    var openTableBody = $('#open_table tbody');
                    openTableBody.empty();
                    var showNextFour = true;
                    var allPricesGreaterThanZero = true;

                    for (var i = 0; i < data.length; i++) {
                        console.log(data);
                        var Line_No = data[i].Line_No;
                        var prospectNo = data[i].Response_No;
                        var docNo = data[i].Tender_No_;
                        var Description = data[i].Description;
                        var Unit_of_Measure = data[i].Unit_of_Measure;
                        var Quantity = data[i].Quantity;
                        var Unit_Price = parseFloat(data[i].Unit_Price);
                        var Amount = parseFloat(data[i].Amount);
                        var Vendor_No_ = data[i].Vendor_No_;
                        var modalHtml =
                            '<div class="modal fade" tabindex="-1" role="dialog" id="financialBid' +
                            Line_No + '">\
                            <div class="modal-dialog modal-lg" role="document">\
                                <div class="modal-content">\
                                    <div class="modal-header">\
                                        <h5 class="modal-title"> Financial Bid - ' + Line_No + '</h5>\
                                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">\
                                            <span aria-hidden="true">&times;</span>\
                                        </button>\
                                    </div>\
                                    <div class="modal-body">\
                                        <div class="money-spinner mx-auto text-center" id="line_spinner' +
                            Line_No + '" style="display: none;">\
                                            <img src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif"\
                                                alt="Loading Gif" style="height: 100px; width: 100px;" class="img-fluid">\
                                        </div>\
                                        <form id="financialBidForm' + Line_No + '">\
                                            {% csrf_token %}\
                                            <input type="hidden" name="prospectNo" id="prospectNo' + Line_No +
                            '" value="' +
                            prospectNo + '">\
                                            <input type="hidden" name="docNo" id="docNo' + Line_No + '" value="' +
                            docNo + '">\
                                            <input type="hidden" name="lineNo" id="lineNo' + Line_No + '" value="' +
                            Line_No + '">\
                            <input type="hidden" name="Vendor_No_" id="Vendor_No_' + Line_No + '" value="' +
                            Vendor_No_ + '">\
                                            <div class="form-group">\
                                                <label>Unit Price</label>\
                                                <div class="input-group">\
                                                    <div class="input-group-prepend">\
                                                        <div class="input-group-text">\
                                                            <i class="fas fa-coins"></i>\
                                                        </div>\
                                                    </div>\
                                                    <input type="text" class="form-control" placeholder="00.00" value=""\
                                                        name="unitPrice" id="unitPrice' + Line_No + '">\
                                                </div>\
                                            </div>\
                                            <div class="form-group my-2">\
                                                <button type="submit" class="btn btn-primary btn-lg btn-block">\
                                                    Submit <i class="fas fa-paper-plane"></i>\
                                                </button>\
                                            </div>\
                                        </form>\
                                    </div>\
                                </div>\
                            </div>\
                        </div>';

                        var row = $('<tr>');
                        row.append($('<td>').text(Description));
                        row.append($('<td>').text(Unit_of_Measure));
                        row.append($('<td>').text(Quantity));
                        row.append($('<td>').text(Unit_Price));
                        row.append($('<td>').text(Amount));


                        if (Unit_Price > 0 && tenderSubmitted == false) {
                            var viewBtn = $('<a>').attr({
                                class: "btn btn-warning text-white financeModal",
                                type: "button",
                                "data-toggle": "modal",
                                "data-target": "#financialBid" + Line_No,
                                id: "SubmitBtnBG" + Line_No,
                            }).text("Update Bid" + ' ');
                        } else if (tenderSubmitted == true) {
                            var viewBtn = $('<a>').attr({
                                class: "btn btn-success text-white",
                            }).text("Submitted" + ' ');

                        } else {
                            var viewBtn = $('<a>').attr({
                                class: "btn btn-primary text-white financeModal",
                                type: "button",
                                "data-toggle": "modal",
                                "data-target": "#financialBid" + Line_No,
                                id: "SubmitBtnBG" + Line_No,
                            }).text("Bid" + ' ');

                        }

                        var icon = $('<i>').addClass('fa fa-coins');
                        viewBtn.append(icon);

                        row.append($('<td>').append(viewBtn));
                        openTableBody.append(row);
                        $('body').append(modalHtml);

                        if (Unit_Price <= 0) {
                            allPricesGreaterThanZero = false;
                            break;
                        }
                    }
                    if (allPricesGreaterThanZero) {
                        console.log('greater');
                        $('.financeStep').addClass('completed');
                        $('#nextTwo').show();
                    } else {
                        $('#nextTwo').show();
                        console.log('smaller');
                    }


                    // initialize DataTables for each table
                    if (!$.fn.DataTable.isDataTable('#open_table')) {
                        $('#open_table').DataTable({
                            "pageLength": 5,
                            "order": [
                                [0, "desc"]
                            ]
                        });
                    }

                    // Bind a click event handler to the button to open the modal
                    $('.financeModal').on('click', function () {
                        var lineNoToOpen = $(this).attr('id').substring(11);
                        $('#financialBid' + lineNoToOpen).modal('show');
                    });
                },
                error: function (xhr, status, error) {
                    console.log("Error:", error);
                },
            });
        }

        function showSpinner(lineNo) {
            $('#line_spinner' + lineNo).show();
        }

        function hideSpinner(lineNo) {
            $('#line_spinner' + lineNo).hide();
        }

        function hideModal(lineNo) {
            $('#financialBid' + lineNo).modal('hide');
        }
        $(document).on("submit", "form[id^='financialBidForm']", function (e) {
            e.preventDefault();

            // Get the CSRF token
            var csrf_token = $(this).find("[name='csrfmiddlewaretoken']").val();

            // Get the parameter values
            var prospectNo = $(this).find("[name='prospectNo']").val();
            var docNo = $(this).find("[name='docNo']").val();
            var lineNo = $(this).find("[name='lineNo']").val();
            var unitPrice = $(this).find("[name='unitPrice']").val();
            var Vendor_No_ = $(this).find("[name='Vendor_No_']").val();

            showSpinner(lineNo);

            $('#line_spinner').show();
            // Send an AJAX post request with the parameter values and the CSRF token
            $.ajax({
                url: "/FinancialBid/" + docNo + "/",
                type: "POST",
                dataType: "json",
                data: {
                    prospectNo: prospectNo,
                    docNo: docNo,
                    lineNo: lineNo,
                    unitPrice: unitPrice,
                    Vendor_No_: Vendor_No_,
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (data) {
                    hideSpinner(lineNo);
                    hideModal(lineNo);
                    FinancialData(documentID);
                    if (data['success'] == true) {
                        iziToast.show({
                            theme: 'dark',
                            backgroundColor: '#239B56',
                            icon: 'las la-check-circle',
                            title: 'Yeah',
                            message: data['message'],
                            position: 'topRight',
                            progressBarColor: '#F4F6F7',
                        });
                    } else {
                        iziToast.show({
                            theme: 'dark',
                            icon: 'las la-exclamation',
                            title: 'Error',
                            message: data['error'],
                            position: 'topRight',
                            progressBarColor: '#ff0800',
                        });
                    }
                },
                error: function (xhr, status, error) {
                    console.log(data);
                    hideSpinner(lineNo);
                    hideModal(lineNo);
                },
            });
        });

        $('#prevOne').click(function () {
            $('#step2').hide(500);
            $('#step1').show(800);
        })
        $('#nextTwo').click(function () {
            $('#step2').hide(500);
            $('.financeStep').addClass('completed')
            if (tenderSubmitted == true) {
                $('#attachmentCodeRow').hide();
                $('#attachmentsRow').hide();
                $('#attachSubmit').hide();
            }

        })



        $attachmentForm.on("submit", (e) => {
            e.preventDefault();
            if ($('#attachmentCode').val() === '') {
                alert('Please fill in all required fields.');
                return false;
            }
            $attachment_spinner.show();
            $attachmentForm.hide();
            var formData = new FormData($attachmentForm[0]);
            let attachments = $('#attachments')[0];
            var attachmentCode = $('#attachmentCode').val();

            for (let i = 0; i < attachments.files.length; i++) {
                formData.append('attachment', attachments.files[i]);
            }

            formData.append('attachmentCode', attachmentCode);

            $.ajax({
                url: "/Attachments/" + documentID + "/",
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                headers: {
                    'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function (data) {
                    $('#attachments').val('');
                    $attachment_spinner.hide();
                    $attachmentForm.show();

                    if (data['success'] == true) {
                        iziToast.show({
                            theme: 'dark',
                            backgroundColor: '#239B56',
                            icon: 'las la-check-circle',
                            title: 'Yeah',
                            message: "Uploaded successfully",
                            position: 'topRight',
                            progressBarColor: '#F4F6F7',
                        });
                        Load_Attachments(documentID);
                        TechnicalRequirementsData(documentID);
                    } else {
                        iziToast.show({
                            theme: 'dark',
                            icon: 'las la-exclamation',
                            title: 'Error',
                            message: "Upload failed: " + data,
                            position: 'topRight',
                            progressBarColor: '#ff0800',
                        });
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    console.log(xhr.responseText);
                    $attachment_spinner.hide();
                    $attachmentForm.show();

                }
            });
        });


        TechnicalRequirementsData(documentID);
        Load_Attachments(documentID);

        $('#prev2').click(function () {
            $('#step2').show(800);
        })
        $('#next3').click(function () {
            if (tenderSubmitted == false) {
                $('#app_sent').hide();
            }

        })

        $submitForm.on("submit", (e) => {
            e.preventDefault();
            $submit_spinner.show();
            $.ajax({
                url: "/Submit/" + documentID + "/",
                type: "POST",
                data: {
                    Process_Type: $('#Process_Type1').val(),
                    TenderType: $('#TenderType1').val(),
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function (data) {
                    $submit_spinner.hide();
                    SecurityData(documentID);
                    if (data['success'] == true) {
                        iziToast.show({
                            theme: 'dark',
                            backgroundColor: '#239B56',
                            icon: 'las la-check-circle',
                            title: 'Yeah',
                            message: data['message'],
                            position: 'topRight',
                            progressBarColor: '#F4F6F7',
                        });
                        $('.completeStep').addClass('completed');
                        $('#submit_first').empty().append('View');
                        $('#app_sent').show();
                    } else {
                        iziToast.show({
                            theme: 'dark',
                            icon: 'las la-exclamation',
                            title: 'Error',
                            message: data['error'],
                            position: 'topRight',
                            progressBarColor: '#ff0800',
                        });
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    console.log(xhr.responseText);
                    $submit_spinner.hide();
                }
            });

        });

        function TechnicalRequirementsData(pk) {
            $("#attachmentsForm select[name='attachmentCode']").find('.after').nextAll().remove();
            $.ajax({
                url: "/TechnicalRequirements/" + pk + "/",
                type: "GET",
                dataType: "json",
                success: function (data) {
                    if (data.length == 0) {
                        $('.technicalStep').hide();
                        $('#step3').show();
                        $('#techStep').hide();

                    }
                    if (data.length > 0) {
                        let options = '';
                        for (var i = 0; i < data.length; i++) {
                            options += '<option value=' + data[i].DocumentCode + '>' + data[i]
                                .DocumentName +
                                '</option>';
                        }
                        $("#attachmentsForm select[name='attachmentCode']").find('.after').after(
                            options);
                    } else {
                        $('.technicalStep').hide();
                    }
                },
                error: function (xhr, status, error) {
                    console.log("Error:", error);
                },
            });
        }


        function Load_Attachments(pk) {
            $.ajax({
                url: "/Attachments/" + pk + "/",
                type: "GET",
                dataType: "json",
                success: function (data) {
                    var containerDiv = $("#attachments-container");
                    containerDiv.empty(); // clear the container div
                    let fileCount = data.length
                    if (fileCount > 0) {
                        $('#attachementCount').empty().append(fileCount);
                        $attachmentBtn.show();
                        for (var i = 0; i < data.length; i++) {
                            var docID = data[i].AuxiliaryIndex2;
                            var tableID = data[i].Table_ID;
                            var attachmentID = data[i].AuxiliaryIndex2;
                            var File_Name = data[i].File_Name;
                            var File_Extension = data[i].File_Extension;
                            // create a new div for this attachment
                            var attachmentDiv = $("<div>", {
                                class: "col-lg-4 col-xl-3"
                            });
                            var fileManBoxDiv = $("<div>", {
                                class: "file-man-box"
                            });
                            // create the form for deleting the attachment
                            var deleteForm = $("<form>", {
                                method: "POST"
                            });
                            if (!tenderSubmitted) {
                                deleteForm.append($("<input>", {
                                    type: "hidden",
                                    name: "docID",
                                    value: docID
                                }));
                                deleteForm.append($("<input>", {
                                    type: "hidden",
                                    name: "tableID",
                                    value: tableID
                                }));
                                var deleteButton = $("<button>", {
                                    class: "file-close",
                                    id: "file-close"
                                }).append($("<i>", {
                                    class: "fa fa-times-circle"
                                }));
                                deleteButton.on("click", function (event) {
                                    event.preventDefault();
                                    $attachment_spinner.show();
                                    $.ajax({
                                        url: '{% url "DeleteAttachment" %}',
                                        type: 'POST',
                                        data: {
                                            docID: docID,
                                            tableID: tableID,
                                            leaveCode: pk,
                                            csrfmiddlewaretoken: $(
                                                    'input[name=csrfmiddlewaretoken]'
                                                )
                                                .val()
                                        },
                                        success: function (data) {
                                            $attachment_spinner.hide();
                                            if (data['success'] == true) {
                                                iziToast.show({
                                                    theme: 'dark',
                                                    backgroundColor: '#239B56',
                                                    icon: 'las la-check-circle',
                                                    title: 'Yeah',
                                                    message: data[
                                                        'message'],
                                                    position: 'topRight',
                                                    progressBarColor: '#F4F6F7',
                                                });
                                                Load_Attachments(pk);
                                                TechnicalRequirementsData(pk);
                                            } else {
                                                iziToast.show({
                                                    theme: 'dark',
                                                    icon: 'las la-exclamation',
                                                    title: 'Error',
                                                    message: data[
                                                        'error'],
                                                    position: 'topRight',
                                                    progressBarColor: '#ff0800',
                                                });
                                            }
                                        },
                                        error: function (error) {
                                            $attachment_spinner.hide();
                                            console.log(error)
                                        }
                                    });
                                });
                                fileManBoxDiv.append(deleteButton);
                            }
                            // create the div for the file icon
                            var fileImgBoxDiv = $("<div>", {
                                class: "file-img-box"
                            }).append($("<img>", {
                                src: "../../static/img/logo/f1.png",
                                alt: "icon"
                            }));
                            fileManBoxDiv.append(fileImgBoxDiv);
                            // create the div for the file name
                            var fileManTitleDiv = $("<div>", {
                                class: "file-man-title"
                            }).append($("<h5>", {
                                class: "mb-0 text-overflow"
                            }).text(File_Name + "." + File_Extension));
                            fileManBoxDiv.append(fileManTitleDiv);
                            attachmentDiv.append(fileManBoxDiv);
                            containerDiv.append(attachmentDiv);
                        }
                    } else {
                        $attachmentBtn.hide();
                    }

                },
                error: function (xhr, status, error) {
                    console.log("Error:", error);
                },
            });
        }

        $attachmentBtn.click(function () {
            $('#leave_attachments_row').toggle(1000);
        })
        $("#Quotation_Deadline")
            .empty().append(moment(
                    '{{response.Quotation_Deadline}}', "YYYY-MM-DD")
                .format(
                    'Do MMM YYYY'));
        $("#Expected_Closing_Time")
            .empty().append(moment(
                    '{{response.Expected_Closing_Time}}',
                    "h:mm:ss a")
                .format(
                    'h:mm a'));
        var procurementStatus = '{{response.Status}}'
        if (procurementStatus == 'New') {
            $('.stepOne').addClass('completed')
        }
    })