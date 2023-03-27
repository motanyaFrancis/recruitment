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