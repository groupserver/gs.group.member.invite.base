jQuery.noConflict()

function popupPreview (event) {
    var baseUri = 'invitationmessage.html', 
        uri = null, 
        messageBody = null, 
        toAddr = null,
        toName = null,
        fromAddr = null,
        subject = null;
    
    messageBody = jQuery('#form\\.message').val();
    uri = baseUri + '?form.message=' + encodeURIComponent(messageBody);
    uri = uri + '&form.fakeHeader=1'
    fromAddr = jQuery('#form\\.fromAddr').val();
    uri = uri + '&form.fromAddr=' + encodeURIComponent(fromAddr);
    toAddr = jQuery('#form\\.toAddr').val();
    uri = uri + '&form.toAddr=' + encodeURIComponent(toAddr);
    toName = jQuery('#form\\.fn').val() || '[Invited Person]';
    uri = uri + '&form.toName=' + encodeURIComponent(toName);
    subject = jQuery('#form\\.subject').val();
    uri = uri + '&form.subject=' + encodeURIComponent(subject);
    
    window.open(uri, 'Message Preview', 
                'height=360,width=730,menubar=no,status=no,toolbar=no,scrollbars=yes');
}

jQuery(window).load( function () {
    jQuery('#invite-message-preview-button').click(popupPreview);
    jQuery('#form\\.fn').focus();
});
