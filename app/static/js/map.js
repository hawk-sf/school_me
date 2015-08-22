L.mapbox.accessToken = 'pk.eyJ1IjoiaGF3ay1zZiIsImEiOiJlZWZiODAxYzA1M2NkOGMyNzc4MmU0MWVmYmIxZDNlMiJ9.xNP0mDW8M6tZ58ZOKRRjTw';

function buildMap() {
  var map = L.mapbox.map('map', 'hawk-sf.n7kjj3ke', { zoomControl: false })
    .setView([37.742, -122.445], 13);
  new L.Control.Zoom({ position: 'topright' }).addTo(map);
}

function getSchools (argument) {
  // body...
}

$(window).on('load', function() {
  buildMap();

  $('#address_modal').modal('show');

  $.validator.addMethod("zipCode", function (value, element) {
      var validZip   = /(^\d{5}$)|(^\d{5}-\d{4}$)/.test(value);
      var sfZipCodes = ['94102','94103','94104','94105','94107','94108','94109',
                        '94110','94111','94112','94114','94115','94116','94117',
                        '94118','94119','94120','94121','94122','94123','94124',
                        '94125','94126','94127','94128','94129','94130','94131',
                        '94132','94133','94134','94137','94139','94140','94141',
                        '94142','94143','94144','94145','94146','94147','94151',
                        '94158','94159','94160','94161','94163','94164','94172',
                        '94177','94188',];
      var localZip   = false;
      if (sfZipCodes.indexOf(value.slice(0, 5)) > -1) {
        localZip = true;
      };

      return this.optional(element) || (validZip);
    }, "Please enter a valid zip (ex: 94110 or 94110-7421)");  

  $('form#address_form').validate({
    rules: {
      zip_code: {
        required: true,
        zipCode:  true
      },
      street: {
        required: false
      }
    },
    highlight: function(element) {
      $(element).closest('.form-group').removeClass('has-success').addClass('has-error');
    },
    unhighlight: function(element) {
      $(element).closest('.form-group').removeClass('has-error').addClass('has-success');
    },
    errorContainer: "#address_error_box",
    errorLabelContainer: "#address_error_box ul",
    wrapper: "li",
    submitHandler: function(form) {
      getSchools();
    }
  });
})

