function getURLParameter (name) {
  return (
    decodeURIComponent(
      (new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(
        location.search
      ) || [null, ''])[1].replace(/\+/g, '%20')
    ) || null
  );
}

// #####################################################
// Open the double map view
//
function open_leaflet () {
  window.location = './viewLeaflet.html?eventid=' + eventid;
}

// #####################################################
// Open the static map view
//
function open_static () {
  window.location = './view.html?eventid=' + eventid;
}

//  #################################################################
//  #  Make table rows clickable
//  ##################################################################
function initTableClick () {
  $(document).ready(function () {
    $('table tbody tr').click(function () {
      document.location = $(this).data('href');
      return false;
    });
  });
}

//  #################################################################
//  #  Find categories of available products for event
//  ##################################################################
function find_unique_cats (productsList) {
  var categoryList = [];

  var productsNumber = productsList.length;

  for (var i = 0; i < productsNumber; i++) {
    if (categoryList.indexOf(productsList[i].cat) === -1) {
      //  indexOf returns -1 if value never occurs in an array
      categoryList.push(productsList[i].cat);
    }
  }

  return categoryList;
}
//  #################################################################
//  #  Writing the table
//  ##################################################################
function listProducts (eventid, productList) {
  var productsNumber = productsList.length;

  var categories = find_unique_cats(productList);
  var categoriesNumber = categories.length;
  var catList = ['Peak Ground Motion Maps', 'Contours and shape files', 'Rasters and grid',
    'Regressions', 'Other files'];

  var baseLink = config_data.dataFolder.path + eventid + '/current/products/';
  var myvar =
    '<table class="table table-hover table-sm archive_table">' +
    '<thead>' +
    '<tr class="table-dark">' +
    '<th style="text-align:left" scope="col";>File name</th>' +
    '<th style="text-align:left" scope="col";>Description</th>' +
    '</thead>' +
    '</tr>' +
    '<tbody>';

  var mapType=0;
  for (var k = 0; k < catList.length; k++) {
    if (categories.indexOf(catList[k]) >= 0) {
      myvar += '<tr data-href="#"><td colspan = "100%" bgcolor="#DA6713" style="text-align:left"><font size="3" color="#ffffff"><b>' + catList[k] +
       '</b></font></td></tr>';
      for (var i = 0; i < productsNumber; i++) {
        if (productsList[i].cat === catList[k]) {

          if (productList[i].name.slice(-4) === '.jpg' && catList[k]==='Peak Ground Motion Maps' && mapType===0) {
            myvar += '<tr data-href="#"><td colspan = "100%" bgcolor="#F6C564" style="text-align:left"><font size="2" color="#ffffff"><b> JPG maps </b></font></td></tr>';
            mapType = 1;
          }
          if (productList[i].name.slice(-4) === '.pdf' && catList[k]==='Peak Ground Motion Maps' && mapType===1) {
            myvar += '<tr data-href="#"><td colspan = "100%" bgcolor="#F6C564" style="text-align:left"><font size="2" color="#ffffff"><b> PDF maps </b></font></td></tr>';
            mapType = 2;
          }

          myvar += '<tr data-href="' + baseLink + productsList[i].name + '">' +
              '<td style="text-align:left"><font size="2"> ' +
              productsList[i].name +
              '</font></td>' +
              '<td style="text-align:left"><font size="2">' +
              productsList[i].desc +
              '</td></font>';
        }
      }
    }
  }
  myvar += '</tbody>' + '</table>';

  document.getElementById('products_table').innerHTML = myvar;

  initTableClick();
}

//  #################################################################
//  #  Main
//  ##################################################################

var eventid = getURLParameter('eventid');

var productsList;
$.getJSON(config_data.dataFolder.path + eventid + '/current/products/productList.json', function (data) {
  productsList = data;
  listProducts(eventid, productsList);
});
