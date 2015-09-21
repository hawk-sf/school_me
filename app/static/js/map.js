function arrayMean(arr) {
  var sum    = 0;
  var length = arr.length;
  for (var i = 0; i < arr.length; i++) {
    sum += arr[i];
  };

  return sum / length;
}

function arrayMedian(arr) {
    arr.sort(function(a,b) {return a - b;});

    var half = Math.floor(arr.length / 2);
    var median;
    if(arr.length % 2) {
        return arr[half];
    } else {
        return (arr[half-1] + arr[half]) / 2.0;
    }
}

function degreeToRadian(deg) {
   return deg * Math.PI / 180;
}

function radianToDegree(rad) {
   return rad * 180 / Math.PI;
}

L.LatLng.prototype.getPointFromDistance = function(bearing, distance) {
  // Reference: http://www.movable-type.co.uk/scripts/latlong.html
  var distance = distance / 6373000;
  var bearing  = degreeToRadian(bearing);

  var lat1 = degreeToRadian(this.lat);
  var lon1 = degreeToRadian(this.lng);
  var lat2 = Math.asin(Math.sin(lat1) * Math.cos(distance) +
                       Math.cos(lat1) * Math.sin(distance) * Math.cos(bearing));
  var lon2 = lon1 + Math.atan2(Math.sin(bearing) * Math.sin(distance) *
                               Math.cos(lat1),
                               Math.cos(distance) - Math.sin(lat1) *
                               Math.sin(lat2));

  return new L.LatLng(radianToDegree(lat2), radianToDegree(lon2));
}

L.Circle.prototype.contains = function(latLng) {
  return this.getLatLng().distanceTo(latLng) < this.getRadius();
}

function getCornerCircleDistance(radius) {
  return Math.sqrt(2 * Math.pow(radius, 2))
}

function getColor(val, max, min) {
  if (val < 0) {
    return '#000000';
  };
  if (min < 0) {
    min = 0;
  };
  var binSize = Math.floor((max - min) / 5);
  return val > max - binSize * 1 ? '#810F7C' :
         val > max - binSize * 2 ? '#8856A7' :
         val > max - binSize * 3 ? '#8C96C6' :
         val > max - binSize * 4 ? '#B3CDE3' :
                                   '#EDF8FB';
}

function getGeoJSONFeature(school) {
  var description = '<i>' + school.levelName + ', ' + school.gradeSpan + '</i><br>';
  description    += school.phone + '<br>';
  description    += school.address + '<br>';
  description    += school.zipCode;
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
                              levelCode:       school.levelCode[0].toLowerCase(),
                              circleArea:      0,
                              dataLabel:       '',
                              filtered:        false
                              }
                };
  return geojson;
}

$(window).on('load', function() {
  L.mapbox.accessToken = $('meta[name=mapbox-access-token]').attr('content');

  var map = L.mapbox.map('map',
                         'hawk-sf.n7kjj3ke',
                         {zoomControl: false}).setView([37.742, -122.445], 13);
  new L.Control.Zoom({ position: 'topright' }).addTo(map);
  var homeLayer   = L.mapbox.featureLayer().addTo(map);
  var workLayer   = L.mapbox.featureLayer().addTo(map);
  var schoolLayer = L.mapbox.featureLayer().addTo(map);
  var circleLayer = L.layerGroup().addTo(map);
  var workCircle  = L.circle();

  var maxData       = 0;
  var minData       = 0;
  var distances     = getPixelDistance();
  var cornerPadding = distances[2] * 10;
  var bounds        = map.getBounds();
  var swLatLng      = bounds.getSouthWest();
  var cornerCircle  = L.circle(
                               swLatLng.getPointFromDistance(45, getCornerCircleDistance(0 + cornerPadding)),
                               0,
                               {
                                color:       '#ffffff',
                                weight:      1,
                                fillColor:   '#c091e6',
                                fillOpacity: 0,
                                id:          'cornerCircle'
                               }
                              ).on('mouseover', function() {
                                this.bringToFront();
                              }).addTo(map);

  var icon  = L.divIcon({
                         html:       '',
                         className:  'dataLabel',
                         iconSize:   [48, 48],
                         iconAnchor: [24, 12],
                         id:         'cornerLabel'
                        });
  var coordinates = swLatLng.getPointFromDistance(45, getCornerCircleDistance(1000 + cornerPadding));
  var cornerLabel = L.marker(coordinates,
                       {
                        icon: icon,
                        id:   'cornerLabel'
                       }).addTo(map);

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
      var dataRange = updateDataCircles();
      updateDataLabels();
      updateDataInfo('Base API', year);

      $.ajax({
        type:  'GET',
        url:   '/api/base_apis/38684780000000_' + year,
      }).success(function(api) {
        updateCornerCircle(api.apib, dataRange[0], dataRange[1]);
        $('button#corner_choice').find('span#choice').text('District Average');
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
      var dataRange = updateDataCircles();
      updateDataLabels();
      updateDataInfo('Growth API', year);

      $.ajax({
        type:  'GET',
        url:   '/api/growth_apis/38684780000000_' + year,
      }).success(function(api) {
        updateCornerCircle(api.growth, dataRange[0], dataRange[1]);
        $('button#corner_choice').find('span#choice').text('District Average');
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
    var dataString = ('street='             + street +
                      '&zip_code='          + zipCode +
                      '&number_of_results=' + '25' +
                      levels);
    $.ajax({
      type: 'GET',
      url:  '/api/map_schools',
      data: dataString
    }).success(function(results) {
      initLayers(codes, results);
      initDataCircles();
      $('#address_modal').modal('hide');
      $('button#submit_address').prop('disabled', false);
      $("form#address_update_form input#zip_code_update").val(zipCode);
      $("form#address_update_form input#street_update").val(street);
      var options = $("form#address_form select#education_level_code :selected")
                    .map(function(){ return this.value }).get();
      $.each(options, function(n, val) {
        $("form#address_update_form select#education_level_code_update option[value="+ val + "]").prop('selected', true)
      });
      $('button#api_button').trigger('click');
    });
  }

  function updateMapSchools() {
    $('button#submit_address_update').prop('disabled', true);
    var zipCode = $("form#address_update_form input#zip_code_update").val();
    var street  = $("form#address_update_form input#street_update").val();
    var limit   = $("form#address_update_form select#number_of_results_update").val();
    var codes   = $("form#address_update_form select#education_level_code_update :selected");
    var levels  = '';
    var pair    = '';
    $.each(codes, function(n, sel) {
      pair    = '&education_level_code=' + $(sel).val();
      levels += pair;
    });
    var dataString = ('street='             + street +
                      '&zip_code='          + zipCode +
                      '&number_of_results=' + limit +
                      levels);
    $.ajax({
      type: 'GET',
      url:  '/api/map_schools',
      data: dataString
    }).success(function(results) {
      schoolLayer.clearLayers();
      circleLayer.clearLayers();
      homeLayer.clearLayers();
      initLayers(codes, results);
      initDataCircles();
      $('button.view_data.btn-info').addClass('btn-default');
      $('button.view_data').removeClass('btn-info');
      $('button#submit_address_update').prop('disabled', false);
      $('a.accordian-toggle').trigger('click');
      $('div#viewed_data_info').hide();
      $('div.corner').hide();
      updateCornerCircle(0,0,0);
    });
  }

  function setCommuteRadius() {
    var zipCode   = $("form#commute_form input#zip_code").val();
    var street    = $("form#commute_form input#street").val();
    var dataString = 'street=' + street + '&zip_code=' + zipCode;

    $.ajax({
      type: 'GET',
      url:  '/api/commute',
      data: dataString
    }).success(function(results) {
      var workGeojson = results['work'];
      workGeojson.properties['title']         = 'Work';
      workGeojson.properties['description']   = workGeojson.place_name;
      workGeojson.properties['marker-color']  = '#a3e46b';
      workGeojson.properties['marker-symbol'] = 'car';
      workLayer.setGeoJSON(workGeojson);
      var allMarkers = []
      $.each([workLayer, homeLayer, schoolLayer], function(idx, layer) {
         layer.eachLayer(function(marker){
           allMarkers.push(marker);
         });
      });
      var totalGroup = L.featureGroup(allMarkers);
      map.fitBounds(totalGroup.getBounds());

      var home   = homeLayer.getLayers()[0];
      var radius = getCommuteCircleRadius();
      workCircle.setLatLng(home.getLatLng())
      workCircle.setRadius(radius);
      workCircle.setStyle({
                           color:       '#7ec9b1',
                           weight:      8,
                           fillOpacity: 0,
                           id:          'commuteCircle'
                          });
      workCircle.addTo(map);
      $('button#view_commute').prop('disabled', false);
      $('button#view_commute').removeClass('btn-default');
      $('button#view_commute').addClass('btn-info');
      $('li#filter_commute_li').show();
      $('li#filter_seperator').show();
    });
  }

  function toggleCommuteCircle() {
    var radius = workCircle.getRadius();
    if (radius > 0) {
      radius = 0;
      $('button#view_commute').addClass('btn-default');
      $('button#view_commute').removeClass('btn-info');
    } else {
      radius = getCommuteCircleRadius();
      $('button#view_commute').removeClass('btn-default');
      $('button#view_commute').addClass('btn-info');
    };
    workCircle.setRadius(radius)
  }

  function getCommuteCircleRadius() {
    var home       = homeLayer.getLayers()[0];
    var work       = workLayer.getLayers()[0];
    var homeLatLng = home.getLatLng();
    var workLatLng = work.getLatLng();
    var radius     = homeLatLng.distanceTo(workLatLng);
    return radius;
  }

  function inCommute(feature) {
    var latLng = L.latLng(feature.geometry.coordinates[0], feature.geometry.coordinates[1]);
    return workCircle.contains(latLng);
  }

  function layerInCommute(layer) {
    var latLng = L.latLng(layer.feature.geometry.coordinates[0], layer.feature.geometry.coordinates[1]);
    return workCircle.contains(latLng);
  }

  function circleInCommute(circle) {
    var latLng = circle.getLatLng();
    return workCircle.contains(latLng);
  }

  function filterCommute() {
    // schoolLayer.setFilter(inCommute(f));    <-- setFilter removes all markers, even if true
    var icon = L.divIcon({
                          html:       '',
                          className:  'emptyIcon',
                          iconSize:   [0 ,0]
                         });
    schoolLayer.eachLayer(function(layer) {
      if (!layerInCommute(layer)) {
        layer.setIcon(icon);
        layer.feature.properties.hidden = true;
      }
    });

    var radius = 0;
    circleLayer.eachLayer(function(circle) {
      if (!circleInCommute(circle)) {
        circle.setRadius(radius);
      }
    });
  }

  function unfilterCommute() {
    // schoolLayer.setFilter(function(f) {    <-- setFilter won't return markers
    //   return true;
    // });
    schoolLayer.eachLayer(function(layer) {
      var icon;
      if (layer.feature.properties.dataLabel == '') {
        icon = L.mapbox.marker.icon({
                                     'marker-color':  '#1087bf',
                                     'marker-symbol': layer.feature.properties.levelCode,
                                    });
      } else {
        var dataLabelClass;
        if (layer.feature.properties.circleArea < 0) {
          dataLabelClass = 'dataLabel-negative';
        } else {
          dataLabelClass = 'dataLabel';
        };
        icon = L.divIcon({
                          html:       layer.feature.properties.dataLabel,
                          className:  dataLabelClass,
                          iconSize:   [48, 48],
                          iconAnchor: [24, 12],
                          id:         layer.feature.properties.cdsCode
                         });
      };
      layer.setIcon(icon);
      layer.feature.properties.hidden = false;
    });

    updateDataCircles();
  }

  function initLayers(codes, results) {
    var featureList = [];
    $.each(codes, function(n, sel) {
      var level       = $(sel).val();
      var geojson;
      $.each(results[level], function(n, feature) {
        geojson = getGeoJSONFeature(feature);
        featureList.push(geojson);
      });
    });
    schoolLayer.setGeoJSON({
        "type":     "FeatureCollection",
        "features": featureList
      });
    map.fitBounds(schoolLayer.getBounds());
    var homeGeojson = results['home'];
    homeGeojson.properties['title']         = 'Home';
    homeGeojson.properties['description']   = homeGeojson.place_name;
    homeGeojson.properties['marker-color']  = '#a3e46b';
    homeGeojson.properties['marker-symbol'] = 'star-stroked';
    homeLayer.setGeoJSON(homeGeojson);
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
                               color:       '#ffffff',
                               weight:      .1,
                               fillColor:   '#c091e6',
                               fillOpacity: 0.75,
                               id:          feature.properties.cdsCode
                              }
                             );
        circleLayer.addLayer(circle);
      } catch(e) {
        console.log(e);
      }
    });
  }

  function updateDataCircles() {
    var geojson   = schoolLayer.getGeoJSON();
    var features  = {};
    var dataArray = [];
    $.each(geojson.features, function(n, feature) {
      features[feature.properties.cdsCode] = feature;
      dataArray.push(feature.properties.circleArea);
    });

    maxData = Math.max.apply(null, dataArray);
    minData = Math.min.apply(null, dataArray);
    var scaler = getCircleScaler();

    circleLayer.eachLayer(function(circle){
      var feature = features[circle.options.id];
      var data    = feature.properties.circleArea;
      var radius  = 0;
      if (!feature.properties.hidden) {
        radius  = Math.sqrt(Math.abs(data * scaler) * 1000/Math.PI);
      };
      circle.setRadius(radius);
      circle.setStyle({
                       color:       '#ffffff',
                       weight:      1,
                       fillColor:   getColor(data, maxData, minData),
                       fillOpacity: 0.75,
                       id:          feature.properties.cdsCode
                      });
    });

    return [maxData, minData];
  }

  function getCircleScaler() {
    if (maxData < 200 || (minData > -200 && minData < 0)) {
      scaler = 20;
    } else {
      scaler = 1;
    };
    return scaler;
  }

  function updateDataLabels() {
    schoolLayer.eachLayer(function(label){
      var dataLabelClass;
      if (label.feature.properties.circleArea < 0) {
        dataLabelClass = 'dataLabel-negative';
      } else {
        dataLabelClass = 'dataLabel';
      }
      var displayLabel = '';
      if (!label.feature.properties.hidden) {
        displayLabel = label.feature.properties.dataLabel;
      };
      var icon = L.divIcon({
                            html:       displayLabel,
                            className:  dataLabelClass,
                            iconSize:   [48, 48],
                            iconAnchor: [24, 12],
                            id:         label.feature.properties.cdsCode
                           });
      label.setIcon(icon);
    });
  }

  function updateDataInfo(dataType, dataYear) {
    $('li#viewed_data_type').find('strong').text(dataType);
    $('li#viewed_data_year').text(dataYear);
    $('div#viewed_data_info').show();
  }

  function updateCornerCircle(circleArea, maxData, minData) {
    var scaler    = getCircleScaler();
    var radius    = Math.sqrt(Math.abs(circleArea * scaler) * 1000/Math.PI);
    distances     = getPixelDistance();
    cornerPadding = distances[2] * 10;
    bounds        = map.getBounds();
    swLatLng      = bounds.getSouthWest();
    cornerCircle.setStyle({
                           color:       'white',
                           weight:      .5,
                           fillColor:   getColor(circleArea, maxData, minData),
                           fillOpacity: 0.75,
                           id:          'cornerCircle'
                          });
    cornerCircle.setRadius(radius);
    cornerCircle.setLatLng(swLatLng.getPointFromDistance(45, getCornerCircleDistance(radius + cornerPadding)))

    cornerLabel.setLatLng(swLatLng.getPointFromDistance(45, getCornerCircleDistance(radius + cornerPadding)));

    if (radius > 0) {
      var icon = L.divIcon({
                        html:       circleArea,
                        className:  'dataLabel',
                        iconSize:   [48, 48],
                        iconAnchor: [24, 12],
                        id:         'cornerLabel'
                       });
      cornerLabel.setIcon(icon);

      var radiusPixels = 2 * radius / distances[0];
      var divPadding   = 10 + radiusPixels;
      $('div.corner').css({
                           'padding-bottom': divPadding + 'px',
                           'padding-left':   divPadding/2 + 'px',
                          });
      $('div.corner').show();
    };
  }

  function getPixelDistance() {
    var centerLatLng = map.getCenter();
    var centerPoint  = map.latLngToContainerPoint(centerLatLng);
    var pointX       = [centerPoint.x + 1, centerPoint.y];
    var pointY       = [centerPoint.x, centerPoint.y + 1];
    var pointDiag    = [centerPoint.x + 1, centerPoint.y + 1];
    var latLngCenter = map.containerPointToLatLng(centerPoint);
    var latLngX      = map.containerPointToLatLng(pointX);
    var latLngY      = map.containerPointToLatLng(pointY);
    var latLngDiag   = map.containerPointToLatLng(pointDiag);
    var distanceX    = latLngCenter.distanceTo(latLngX);
    var distanceY    = latLngCenter.distanceTo(latLngY);
    var distanceDiag = latLngCenter.distanceTo(latLngDiag);
    return [distanceX, distanceY, distanceDiag]
  }

  function getCircleAreas() {
    var geojson   = schoolLayer.getGeoJSON();
    var dataArray = [];
    $.each(geojson.features, function(n, feature) {
      dataArray.push(feature.properties.circleArea);
    });

    return dataArray;
  }

  function getStats(recordType, year, statType) {
    console.log(recordType, year, statType)
    $.ajax({
      type: 'GET',
      url:  '/api/stats/' + recordType + '/' + year,
    }).success(function(stats) {
      var dataArray = getCircleAreas();
      var maxData   = Math.max.apply(null, dataArray);
      var minData   = Math.min.apply(null, dataArray);
      updateCornerCircle(Math.floor(stats[statType]), maxData, minData);
    });
  }

  function getSchoolsMean() {
    var dataArray = getCircleAreas();
    var mean      = arrayMean(dataArray);
    var maxData   = Math.max.apply(null, dataArray);
    var minData   = Math.min.apply(null, dataArray);
    updateCornerCircle(Math.floor(mean), maxData, minData); 
  }

  function getSchoolsMedian() {
    var dataArray = getCircleAreas();
    var median    = arrayMedian(dataArray);
    var maxData   = Math.max.apply(null, dataArray);
    var minData   = Math.min.apply(null, dataArray);
    updateCornerCircle(Math.floor(median), maxData, minData); 
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
      goodZip = validZip && localZip;

      return this.optional(element) || (localZip);
    }, "Please enter a valid SF zip (ex: 94110 or 94110-7421)");

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

  $('form#address_update_form').validate({
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
      number_of_results: {
        required: false
      }
    },
    highlight: function(element) {
      $(element).closest('.form-group').removeClass('has-success').addClass('has-error');
    },
    unhighlight: function(element) {
      $(element).closest('.form-group').removeClass('has-error').addClass('has-success');
    },
    errorContainer: "#address_update_error_box",
    errorLabelContainer: "#address_update_error_box ul",
    wrapper: "li",
    submitHandler: function(form) {
      updateMapSchools();
    }
  });

  $('form#commute_form').validate({
    rules: {
      zip_code: {
        required: true,
        zipCode:  true
      },
      street: {
        required: true
      }
    },
    highlight: function(element) {
      $(element).closest('.form-group').removeClass('has-success').addClass('has-error');
    },
    unhighlight: function(element) {
      $(element).closest('.form-group').removeClass('has-error').addClass('has-success');
    },
    errorContainer: "#commute_update_error_box",
    errorLabelContainer: "#commute_update_error_box ul",
    wrapper: "li",
    submitHandler: function(form) {
      setCommuteRadius();
    }
  });

  $('body').on('click', 'button#submit_commute', function(e) {
    e.stopPropagation();
  });

  $('body').on('click', 'button#view_commute', function(e) {
    e.stopPropagation();
    toggleCommuteCircle();
  });

  $('body').on('click', 'a#filter_commute', function(e) {
    e.stopPropagation();
    filterCommute();
    $('li#unfilter_commute_li').show();
    $('li#filter_commute_li').hide();
  });

  $('body').on('click', 'a#unfilter_commute', function(e) {
    e.stopPropagation();
    unfilterCommute();
    $('li#filter_commute_li').show();
    $('li#unfilter_commute_li').hide();
  });

  $('body').on('click', 'button#api_button', function(e) {
    $('div#base_api_year_select').show();
    $('div#growth_api_year_select').show();
  });

  $('body').on('click','a#base_api_year_options', function(e) {
    e.stopPropagation();
    $('#base_api_year_select').toggle();
  });

  $('select#base_api_year').click(function (e) {
    e.stopPropagation();
  });

  $('body').on('click', 'button.view_data', function(e) {
    $('button.view_data.btn-info').addClass('btn-default');
    $('button.view_data').removeClass('btn-info');
    $(this).removeClass('btn-default');
    $(this).addClass('btn-info');
  });

  $('body').on('change', 'select.change_data', function(e) {
    $('button.view_data.btn-info').addClass('btn-default');
    $('button.view_data').removeClass('btn-info');
  });

  $('body').on('click','button#view_base_api', function(e) {
    e.stopPropagation();
    $('button.view_data').prop('disabled', true);
    var year = $("select#base_api_year").val();
    getBaseAPIs(year);
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
    $('button.view_data').prop('disabled', false);
  });

  $('body').on('click','a#view_district_avg', function(e) {
    $('.view_data').prop('disabled', true);
    var recordTypeMapper = {
                            'Base API':   'base_apis',
                            'Growth API': 'growth_apis',
                           }
    var record = $('li#viewed_data_type').find('strong').text();
    var year   = $('li#viewed_data_year').text();
    getStats(recordTypeMapper[record], year, 'mean');
    $('button#corner_choice').find('span#choice').text('District Average');
    $('.view_data').prop('disabled', false);
  });

  $('body').on('click','a#view_district_med', function(e) {
    $('.view_data').prop('disabled', true);
    var recordTypeMapper = {
                            'Base API':   'base_apis',
                            'Growth API': 'growth_apis',
                           }
    var record = $('li#viewed_data_type').find('strong').text();
    var year   = $('li#viewed_data_year').text();
    getStats(recordTypeMapper[record], year, 'median');
    $('button#corner_choice').find('span#choice').text('District Median');
    $('.view_data').prop('disabled', false);
  });

  $('body').on('click','a#view_schools_avg', function(e) {
    $('.view_data').prop('disabled', true);
    getSchoolsMean();
    $('button#corner_choice').find('span#choice').text('Displayed Schools Average');
    $('.view_data').prop('disabled', false);
  });

  $('body').on('click','a#view_schools_med', function(e) {
    $('.view_data').prop('disabled', true);
    getSchoolsMedian();
    $('button#corner_choice').find('span#choice').text('Displayed Schools Median');
    $('.view_data').prop('disabled', false);
  });

  $('select#growth_api_year').click(function (e) {
    e.stopPropagation();
  });

  $('body').on('click','span.get_more_info', function(e) {
    e.stopPropagation();
    $('#explanation_modal').modal('show');
  });

  map.on('move', function() {
    var radius = cornerCircle.getRadius();
    var scaler = getCircleScaler();
    var area   = (Math.PI * Math.pow(radius, 2)) / scaler / 1000;

    var dataArray = getCircleAreas();
    var maxData   = Math.max.apply(null, dataArray);
    var minData   = Math.min.apply(null, dataArray);

    updateCornerCircle(Math.floor(area), maxData, minData);
  });
})
