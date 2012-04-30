$('#frmPostIdentify').submit(function() {
    // var queryString = $('#frmPostIdentify').formSerialize();
    // $.post('/v1/identify', queryString);

    $('#frmPostIdentify').ajaxForm();
});

$('#frmPostConvert').submit(function() {
    // var queryString = $('#frmPostConvert').formSerialize();
    // $.post('/v1/convert', queryString);

    $('#frmPostConvert').ajaxForm();
});

