L.mapbox.accessToken = 'pk.eyJ1IjoiaGF3ay1zZiIsImEiOiJlZWZiODAxYzA1M2NkOGMyNzc4MmU0MWVmYmIxZDNlMiJ9.xNP0mDW8M6tZ58ZOKRRjTw';

function getGeoJSONFeature(school) {
  var description = '<i>' + school.levelName + ', ' + school.gradeSpan + '</i><br>';
  description    += school.phone + '<br>';
  description    += school.address + '<br>';
  description    += school.zipCode + '<br>';
  description    += school.website;
  var geojson = {
                 type: 'Feature',
                 geometry: {
                              type:        'Point',
                              coordinates: [
                                            parseFloat(school.longitude),
                                            parseFloat(school.latitude)
                                           ]
                             },
                 properties: {
                              title:           school.school,
                              description:     description,
                              cdsCode:         school.cdsCode,
                              'marker-color':  '#1087bf',
                              'marker-symbol': school.levelCode[0].toLowerCase(),
                              circleArea:      0,
                              dataLabel:       ''
                              }
                };
  return geojson;
}

$(window).on('load', function() {
  var map = L.mapbox.map('map',
                         'hawk-sf.n7kjj3ke',
                         {zoomControl: false}).setView([37.742, -122.445], 13);
  new L.Control.Zoom({ position: 'topright' }).addTo(map);
  var schoolLayer = L.mapbox.featureLayer().addTo(map);
  var circleLayer = L.layerGroup().addTo(map);
  var labelLayer  = L.layerGroup().addTo(map);

  function getSchool(cdsCode) {
    $.ajax({
      type: 'GET',
      url:  '/api/schools/' + cdsCode,
    }).success(function(school) {
      var geojson     = getGeoJSONFeature(school);
      var schoolLayer = L.mapbox.featureLayer().addTo(map);
      schoolLayer.setGeoJSON(geojson);
    });
  }

  function getBaseAPIs(year) {
    var geojson     = schoolLayer.getGeoJSON();
    var cdsCodes    = '';
    var pair        = '';
    $.each(geojson.features, function(n, feature) {
      pair      = '&cds_codes=' + feature.properties.cdsCode;
      cdsCodes += pair;
    });
    var dataString = 'year=' + year + cdsCodes;
    $.ajax({
      type:  'GET',
      url:   '/api/base_apis',
      data:  dataString
    }).success(function(apis) {
      res = {};
      $.each(apis['results'], function(n, api) {
         res[api.cds] = api;
      })
      $.each(geojson.features, function(n, feature) {
        try {
          feature.properties.circleArea = res[feature.properties.cdsCode].apib;
          feature.properties.dataLabel  = res[feature.properties.cdsCode].apib.toString();
        } catch (e) {
          feature.properties.circleArea = 0;
          feature.properties.dataLabel  = '';
          console.log(e);
        }
      });
    });
  }

  function getGrowthAPIs(year) {
    var geojson     = schoolLayer.getGeoJSON();
    var cdsCodes    = '';
    var pair        = '';
    $.each(geojson.features, function(n, feature) {
      pair      = '&cds_codes=' + feature.properties.cdsCode;
      cdsCodes += pair;
    });
    var dataString = 'year=' + year + cdsCodes;
    $.ajax({
      type:  'GET',
      url:   '/api/growth_apis',
      data:  dataString
    }).success(function(apis) {
      res = {};
      $.each(apis['results'], function(n, api) {
         res[api.cds] = api;
      })
      $.each(geojson.features, function(n, feature) {
        try {
          feature.properties.circleArea = res[feature.properties.cdsCode].growth;
          feature.properties.dataLabel  = res[feature.properties.cdsCode].growth.toString();
        } catch (e) {
          feature.properties.circleArea = 0;
          feature.properties.dataLabel  = '';
          console.log(e);
        }
      });
    }); 
  }

  function getMapSchools() {
    $('button#submit_address').prop('disabled', true);
    var zipCode = $("form#address_form input#zip_code").val();
    var street  = $("form#address_form input#street").val();
    var codes   = $("form#address_form select#education_level_code :selected");
    var levels  = '';
    var pair    = '';
    $.each(codes, function(n, sel) {
      pair    = '&education_level_code=' + $(sel).val();
      levels += pair;
    });
    var dataString = ('street='    + street +
                      '&zip_code=' + zipCode +
                      levels);
    $.ajax({
      type: 'GET',
      url:  '/api/map_schools',
      data: dataString
    }).success(function(results) {
      $.each(codes, function(n, sel) {
        var level       = $(sel).val();
        var featureList = [];
        var geojson;
        $.each(results[level], function(n, feature) {
          geojson = getGeoJSONFeature(feature);
          featureList.push(geojson);
        });
        schoolLayer.setGeoJSON({
          "type":     "FeatureCollection",
          "features": featureList
        });
        map.fitBounds(schoolLayer.getBounds());
      });
      var homeLayer   = L.mapbox.featureLayer().addTo(map);
      var homeGeojson = results['home'];
      homeGeojson.properties['title']         = 'Home';
      homeGeojson.properties['description']   = homeGeojson.place_name;
      homeGeojson.properties['marker-color']  = '#a3e46b';
      homeGeojson.properties['marker-symbol'] = 'star-stroked';
      homeLayer.setGeoJSON(homeGeojson);
      initDataCircles();
      initDataLabels();
      $('#address_modal').modal('hide');
      $('button#submit_address').prop('disabled', false);
    });
  }

  function initDataCircles() {
    var geojson = schoolLayer.getGeoJSON();
    $.each(geojson.features, function(n, feature) {
      var radius = Math.sqrt(feature.properties.circleArea * 1000/Math.PI);
      try {
        var circle = L.circle(
                              feature.geometry.coordinates.reverse(),
                              radius,
                              {
                               color:       'purple',
                               weight:      .5,
                               fillColor:   '#c091e6',
                               fillOpacity: 0.75,
                               id:          feature.properties.cdsCode
                              }
                             ).bindPopup(feature.properties.circleArea.toString());
        circleLayer.addLayer(circle);
      } catch(e) {
        console.log(e);
      }
    });
  }

  function updateDataCircles() {
    console.log('update')
    var geojson = schoolLayer.getGeoJSON();
    var circles = circleLayer.getLayers();
    var features = {};
    $.each(geojson.features, function(n, feature) {
      features[feature.properties.cdsCode] = feature;
    });
    circleLayer.eachLayer(function(circle){
      var feature = features[circle.options.id];
      console.log('updating ', feature.properties.title)
      var radius = Math.sqrt(feature.properties.circleArea * 1000/Math.PI);
      circle.setRadius(radius);
    });
  }

  function initDataLabels() {
    var geojson = schoolLayer.getGeoJSON();
    $.each(geojson.features, function(n, feature) {
      try {
        var icon  = L.divIcon({
                               html:       feature.properties.dataLabel,
                               className:  'dataLabel',
                               iconSize:   [36, 36],
                               iconAnchor: [18,-6],
                               id:         feature.properties.cdsCode
                              });
        var coordinates = feature.geometry.coordinates.reverse();
        coordinates[1] -= 0.01;
        var label = L.marker(coordinates,
                             {
                              icon: icon,
                              zIndexOffset: 1000,
                              id:   feature.properties.cdsCode
                             }).addTo(map);
        labelLayer.addLayer(label);
      } catch (e) {
        console.log(e);
      }
    });
  }

  function updateDataLabels() {
    var geojson  = schoolLayer.getGeoJSON();
    var labels   = labelLayer.getLayers();
    var features = {};
    $.each(geojson.features, function(n, feature) {
      features[feature.properties.cdsCode] = feature;
    });
    labelLayer.eachLayer(function(label){
      var feature = features[label.options.id];
      var icon    = L.divIcon({
                                 html:       feature.properties.dataLabel,
                                 className:  'dataLabel',
                                 iconSize:   [36, 36],
                                 iconAnchor: [18,-6],
                                 id:         feature.properties.cdsCode
                                });
      label.setIcon(icon);
    });
  }

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
      },
      education_level_code: {
        required: true,
      },
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
      getMapSchools();
    }
  });

  $('body').on('click','a#base_api_year_options', function(e) {
    e.stopPropagation();
    $('#base_api_year_select').toggle();
  });

  $('select#base_api_year').click(function (e) {
    e.stopPropagation();
  });

  $('body').on('click','button#view_base_api', function(e) {
    e.stopPropagation();
    $('button.view_data').prop('disabled', true);
    var year = $("select#base_api_year").val();
    getBaseAPIs(year);
    updateDataCircles();
    updateDataLabels();
    $('button.view_data').prop('disabled', false);
  });

  $('body').on('click','a#growth_api_year_options', function(e) {
    e.stopPropagation();
    $('#growth_api_year_select').toggle();
  });

  $('body').on('click','button#view_growth_api', function(e) {
    e.stopPropagation();
    $('button.view_data').prop('disabled', true);
    var year = $("select#growth_api_year").val();
    getGrowthAPIs(year);
    updateDataCircles();
    updateDataLabels();
    $('button.view_data').prop('disabled', false);
  });

  $('select#growth_api_year').click(function (e) {
    e.stopPropagation();
  });

  $('body').on('click', 'button#clear_button', function() {
    circleLayer.clearLayers();
    $('div.dataLabel').remove();
    labelLayer.clearLayers();
  });

  $('body').on('click', 'button#log_button', function() {
    var geojson = schoolLayer.getGeoJSON();
    console.log("Features");
    schoolLayer.eachLayer(function(layer){
      console.log(layer)
    })
    console.log("Circles")
    circleLayer.eachLayer(function(layer){
      console.log(layer);
    });
    console.log("Data")
    labelLayer.eachLayer(function(layer){
      console.log(layer);
    });
  });
})

