/*

 Copyright 2018, GeoSolutions Sas.
 All rights reserved.

 This source code is licensed under the BSD-style license found in the
 LICENSE file in the root directory of this source tree.

*/


function addItem() {
    var text = $.trim($('#add').val());
    if (text) {
        var li = $('<li/>')
        .text(text)
        .on("click", function() { $(this).remove()});
        $('#organizations').prepend(
            li.addClass('org-item btn border border-secondary m-1')
        );
        $('#add').val('');
    }
};

$('.modal').on('hidden.bs.modal', function() {
    $(this).find('form')[0].reset();
    $(this).find('li').remove();
    $('#errors').hide();
});

$('.submit-btn').click(function() {

    var user_first_name = $('#user-first-name').val();
    var user_last_name = $('#user-last-name').val();
    var user_fiscal_code = $('#user-fiscal-code').val();
    var user_role = $('#user-role').val();
    var organizations = $('#organizations > li').map(function() {
        return this.innerHTML;
    }).get();

    if(user_fiscal_code) {
        var regex = /^(?:(?:[B-DF-HJ-NP-TV-Z]|[AEIOU])[AEIOU][AEIOUX]|[B-DF-HJ-NP-TV-Z]{2}[A-Z]){2}[\dLMNP-V]{2}(?:[A-EHLMPR-T](?:[04LQ][1-9MNP-V]|[1256LMRS][\dLMNP-V])|[DHPS][37PT][0L]|[ACELMRT][37PT][01LM])(?:[A-MZ][1-9MNP-V][\dLMNP-V]{2}|[A-M][0L](?:[1-9MNP-V][\dLMNP-V]|[0L][1-9MNP-V]))[A-Z]$/i;
        if (regex.test(user_fiscal_code)) {
            var host = location.protocol
            .concat('//')
            .concat(window.location.host);
            var json_data = {
                user_first_name: user_first_name,
                user_last_name: user_last_name,
                user_fiscal_code: user_fiscal_code,
                user_role: user_role,
                organizations: organizations
            };
            $.ajax({
                url: host.concat('/api/auth/'),
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(json_data),
                success: function (data) {
                   location.reload();
                },
                error: function (data) {
                    $('#errors').show();
                    $('#errors').text(data.responseText.split('"')[1]);
                }
            });
        } else {
            $('#errors').show();
            $('#errors').text('Codice Fiscale dell\'utente non valido');
        }
    } else {
        $('#errors').show();
        $('#errors').text('Campo Codice Fiscale obbligaotrio.');
    }

});