function loadHobby() {
    $.ajax({
        url: '{% url "QyApplicantHobbies" %}',
        type: "GET",
        dataType: "json",
        success: function (data) {
            var tableBody = $('#hobbyTable tbody');
            tableBody.empty(); // clear existing rows if any
            // iterate through the data and append to the table
            for (var i = 0; i < data[1].length; i++) {
                var Hobbies = data[1][i].Hobbies;
                var MembershipNo = data[1][i].MembershipNo;
                var Description = data[1][i].Description;
                var Line_No = data[1][i].Line_No;

                var row = $('<tr>');

                row.append($('<td>').text(Hobbies));
                // Create the form with inputs and submit button
                var form = $('<form>').attr({
                    method: 'POST',
                    action: '{% url "FnApplicantHobby" %}'
                }).append('{% csrf_token %}');

                var hobbyInput = $('<input>').attr({
                    type: 'hidden',
                    name: 'hobby',
                    value: Hobbies
                });
                var lineNoInput = $('<input>').attr({
                    type: 'hidden',
                    name: 'lineNo',
                    value: Line_No
                });
                var myActionInput = $('<input>').attr({
                    type: 'hidden',
                    name: 'myAction',
                    value: 'delete'
                });
                var submitBtn = $('<button>').attr({
                    type: 'submit',
                    class: 'btn btn-danger'
                }).text('delete');

                // Handle form submission
                form.submit(function (event) {
                    event.preventDefault(); // prevent default form submission
                    $.ajax({
                        url: form.attr('action'),
                        type: form.attr('method'),
                        data: form.serialize(),
                        success: function (data) {
                            loadHobby();
                            if (data['success'] == true) {
                                iziToast.show({
                                    theme: 'dark',
                                    backgroundColor: '#239B56',
                                    icon: 'las la-check-circle',
                                    message: data['message'] + " " +
                                        "deleted",
                                    position: 'topRight',
                                    progressBarColor: '#F4F6F7',
                                });
                            } else {
                                iziToast.show({
                                    theme: 'dark',
                                    icon: 'las la-exclamation',
                                    title: 'Error',
                                    message: data['message'],
                                    position: 'topRight',
                                    progressBarColor: '#ff0800',
                                });
                            }
                        },
                        error: function (xhr, status, error) {
                            console.log("Error:", error);
                            iziToast.show({
                                theme: 'dark',
                                icon: 'las la-exclamation',
                                title: 'Error',
                                message: 'CSRF verification failed. Request aborted.',
                                position: 'topRight',
                                progressBarColor: '#ff0800',
                            });
                        }
                    });
                });

                var td = $('<td>').append(form.append(hobbyInput, lineNoInput, myActionInput,
                    submitBtn));
                row.append(td);

                // Append the new row to the table
                $('#hobbyTable tbody').append(row);
            }
            // initialize DataTables for each table
            if (!$.fn.DataTable.isDataTable('#hobbyTable')) {
                $('#hobbyTable').DataTable({
                    "pageLength": 5,
                    "order": [
                        [0, "desc"]
                    ]
                });
            }

        },
        error: function (xhr, status, error) {
            console.log("Error:", error);
        },
    });
}