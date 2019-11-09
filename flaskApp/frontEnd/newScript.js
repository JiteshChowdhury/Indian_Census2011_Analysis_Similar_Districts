var map;
var category = null;
var states = [];
var responseData = {};
var subCategory = null;
AmCharts.ready( function() {
    map = new AmCharts.AmMap();
    map.panEventsEnabled = true;
    map.backgroundColor = "#F2DFD8";
    map.backgroundAlpha = 1;

    map.zoomControl.panControlEnabled = false;
    map.zoomControl.zoomControlEnabled = false;
    map.zoomControl.homeButtonEnabled = false;

    var dataProvider = {
        map: "indiaLow",
        getAreasFromMap: true
    };

    map.dataProvider = dataProvider;

    map.areasSettings = {
        autoZoom: false,
        color: "#BFAAA3",
        colorSolid: "#BFAAA3",
        selectedColor: "#40312E",
        outlineColor: "#F2DFD8",
        rollOverColor: "#A68477",
        rollOverOutlineColor: "#A68477",
        selectable: true
    };

    map.addListener( 'clickMapObject', function( event ) {
        // deselect the area by assigning all of the dataProvider as selected object
        map.selectedObject = map.dataProvider;

        // toggle showAsSelected
        event.mapObject.showAsSelected = !event.mapObject.showAsSelected;

        // bring it to an appropriate color
        map.returnInitialColor( event.mapObject );

        // let's build a list of currently selected states
        states = [];
        for ( var i in map.dataProvider.areas ) {
            var area = map.dataProvider.areas[ i ];
            if ( area.showAsSelected ) {
                states.push( area.title );
            }
        }
        category = null;
        subCategory = null;
        if(states.length == 2){
          document.getElementById("submitButton").disabled = false;
        }
        else{
          document.getElementById("submitButton").disabled = true;
        }
        console.log(states);
    } );
    map.export = {
        enabled: true
    }

    map.write( "mapdiv" );

} );

// dropdown

$(function() {
    $("#text-one").change(function() {
        $("#text-two").load("textdata/" + $(this).val() + ".txt");
    });
});

function setCategory(){
  category = document.getElementById('text-one').value;
}

function setSubCategory(){
  subCategory = document.getElementById('text-two').value;
}

$(document).ready(function(){
    $("button").click(function(){
        // Get value from input element on the page
        var state1 = states[0];
        var state2 = states[1];
        $("#result").hide();
        $("#chartdiv").hide();
        $("#checking").show();
        if(category){
          if(subCategory){
              $.get("http://127.0.0.1:8080/census", {s1: state1, s2: state2, selectedCategory: category, selectedSubCategory: subCategory} , function(data){
              responseData = data;
              // Display the returned data in browser
              $("#checking").hide();
              $("#result").show();
              $("#chartdiv").show();
              $("#result").html(data.Similarity);
              subCategory = null;
              heat();
            })
          }
          else{
              $.get("http://127.0.0.1:8080/census", {s1: state1, s2: state2, selectedCategory: category} , function(data){
              responseData = data;
              // Display the returned data in browser
              
              $("#checking").hide();
              $("#result").show();
              $("#chartdiv").show();
              $("#result").html(data.Similarity);
              heat();
            });
          }
          
        }
        // Send the input data to the server using get
        else{
            $.get("http://127.0.0.1:8080/census", {s1: state1, s2: state2} , function(data){
              responseData = data;
              // Display the returned data in browser
              
              $("#checking").hide();
              $("#result").show();
              $("#chartdiv").show();
              $("#result").html(data.Similarity);
              heat();
            });
        }
        
    });
    
});

function heat(){
    am4core.ready(function() {

        // Themes begin
        am4core.useTheme(am4themes_animated);
        // Themes end
        
        var chart = am4core.create("chartdiv", am4charts.XYChart);
        chart.maskBullets = false;
        
        var xAxis = chart.xAxes.push(new am4charts.CategoryAxis());
        var yAxis = chart.yAxes.push(new am4charts.CategoryAxis());
        
        xAxis.dataFields.category = "State One";
        yAxis.dataFields.category = "State Two";
        
        xAxis.renderer.grid.template.disabled = true;
        xAxis.renderer.minGridDistance = 20;
        
        yAxis.renderer.grid.template.disabled = true;
        yAxis.renderer.inversed = true;
        yAxis.renderer.minGridDistance = 15;
        
        var series = chart.series.push(new am4charts.ColumnSeries());
        series.dataFields.categoryX = "State One";
        series.dataFields.categoryY = "State Two";
        series.dataFields.value = "value";
        series.sequencedInterpolation = true;
        series.defaultState.transitionDuration = 3000;
        
        var bgColor = new am4core.InterfaceColorSet().getFor("background");
        
        var columnTemplate = series.columns.template;
        columnTemplate.strokeWidth = 1;
        columnTemplate.strokeOpacity = 0.2;
        columnTemplate.stroke = bgColor;
        columnTemplate.tooltipText = "{State One}, {State Two}: {value.workingValue.formatNumber('#.######')}";
        columnTemplate.width = am4core.percent(100);
        columnTemplate.height = am4core.percent(100);
        
        series.heatRules.push({
          target: columnTemplate,
          property: "fill",
          min: am4core.color("#BFAAA3"),
          max: am4core.color("#40312E")
        });
        
        // heat legend
        var heatLegend = chart.bottomAxesContainer.createChild(am4charts.HeatLegend);
        heatLegend.width = am4core.percent(100);
        heatLegend.series = series;
        heatLegend.valueAxis.renderer.labels.template.fontSize = 9;
        heatLegend.valueAxis.renderer.minGridDistance = 30;
        
        // heat legend behavior
        series.columns.template.events.on("over", function(event) {
          handleHover(event.target);
        })
        
        series.columns.template.events.on("hit", function(event) {
          handleHover(event.target);
        })
        
        function handleHover(column) {
          if (!isNaN(column.dataItem.value)) {
            heatLegend.valueAxis.showTooltipAt(column.dataItem.value)
          }
          else {
            heatLegend.valueAxis.hideTooltip();
          }
        }
        
        series.columns.template.events.on("out", function(event) {
          heatLegend.valueAxis.hideTooltip();
        })
        
        chart.data = responseData.Data;
    });
}