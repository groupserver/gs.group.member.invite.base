jQuery.noConflict()

function popupPreview (event) {
    var baseUri = 'invitationmessage.html', 
        uri = null, 
        messageBody = null, 
        toAddr = null,
        toname = null
        fromAddr = null,
        subject = null;
    
    messageBody = jQuery('#form\\.message').val();
    messageBody = messageBody.replace(/\ /g, '%20');
    messageBody = messageBody.replace(/\n/g, '%0A');
    uri = baseUri + '?form.message=' + messageBody;
    fromAddr = jQuery('#form\\.fromAddr').val();
    uri = uri + '&form.fromAddr=' + fromAddr;
    toAddr = jQuery('#form\\.toAddr').val();
    uri = uri + '&form.toAddr=' + toAddr;
    toName = jQuery('#form\\.fn').val() || '[Invited Person]';
    uri = uri + '&form.toName=' + toName;
    subject = jQuery('#form\\.subject').val();
    uri = uri + '&form.subject=' + subject.replace(/ /g, '%20');
    
    window.open(uri, 'Message Preview', 
                'height=360,width=730,menubar=no,status=no,toolbar=no,scrollbars=yes');
}

jQuery(window).load( function () {
    jQuery('#invite-message-preview-button').click(popupPreview);
    jQuery('#form\\.fn').focus();
});
