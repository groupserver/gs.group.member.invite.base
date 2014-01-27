jQuery.noConflict();function popupPreview(e){var g="invitationmessage.html",d=null,h=null,f=null,b=null,a=null,c=null;
h=jQuery("#form\\.message").val();d=g+"?form.message="+encodeURIComponent(h);d=d+"&form.fakeHeader=1";
a=jQuery("#form\\.fromAddr").val();d=d+"&form.fromAddr="+encodeURIComponent(a);f=jQuery("#form\\.toAddr").val();
d=d+"&form.toAddr="+encodeURIComponent(f);b=jQuery("#form\\.fn").val()||"[Invited Person]";
d=d+"&form.toName="+encodeURIComponent(b);c=jQuery("#form\\.subject").val();d=d+"&form.subject="+encodeURIComponent(c);
window.open(d,"Message Preview","height=360,width=730,menubar=no,status=no,toolbar=no,scrollbars=yes")
}jQuery(window).load(function(){jQuery("#invite-message-preview-button").click(popupPreview);
jQuery("#form\\.fn").focus()});