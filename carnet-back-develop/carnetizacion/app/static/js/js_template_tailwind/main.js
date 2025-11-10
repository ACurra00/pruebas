(function ($) {
	("use strict");

  var windowOn = $(window);
	////////////////////////////////////////////////////
	// PreLoader Js start
	windowOn.on("load", function () {
    $("#loading").fadeOut(500);
	});
  // PreLoader Js end


  // Quantity Js start
  $(".q-minus").click(function () {
    var $input = $(this).parent().find("input");
    var count = parseInt($input.val()) - 1;
    count = count < 1 ? 1 : count;
    $input.val(count);
    $input.change();
    return false;
  });
  $(".q-plus").click(function () {
    var $input = $(this).parent().find("input");
    $input.val(parseInt($input.val()) + 1);
    $input.change();
    return false;
  });
  // Quantity Js end

  // metismenu activation start 
  $("#metismenu").metisMenu();
  // metismenu activation end 
  
  // niceSelect activation start 
  $('select').niceSelect();
  // niceSelect activation end 
  
  // chart activation start
  if (jQuery("#chart").length > 0) {
    var options = {
          series: [
            {
              name: "Expense",
              data: [15, 65, 85, 45, 100, 75, 100, 55, 120, 140, 100, 165]
            },
            {
              name: "Income",
              data: [35, 95, 45, 32, 85, 120, 41, 140, 160, 100, 180, 195]
            }
          ],
          chart: {
            height: 445,
            width: '100%',
            type: "area",
          },
          dataLabels: {
            enabled: true
          },
          title: {
            text: "Cashflow",
            align: "left",
          },
          colors: ["#E95582", "#6F4EF6"],
          stroke: {
            curve: "smooth"
          },
          xaxis: {
            categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
          },
          yaxis: {
            min: 10,
            max: 200
          },
          legend: {
            position: "top",
            horizontalAlign: "right",
            floating: true,
            offsetY: -25,
            offsetX: -5
          }
    }

    var chart = new ApexCharts(document.querySelector("#chart"), options);


    setTimeout(function() { chart.render(); }, 300);
  }
  // chart activation end


  // chartBar activation start
  if (jQuery("#chartBar").length > 0) {
    var optionsChartBar = {
      series: [
        {
          name: "Expense",
          data: [20, 45, 85, 100, 120, 160]
        },
        {
          name: "Income",
          data: [56, 80, 95, 125, 150, 190]
        }
      ],
      chart: {
        type: "bar",
        height: 500,
        width: '100%',
      },
      title: {
        text: "Expense vs Income",
        align: "left",
      },
      dataLabels: {
        enabled: false
      },
      colors: ["#E8E4F5", "#6F4EF6"],
      stroke: {
        show: true,
        width: 2,
        colors: ["transparent"]
      },
      xaxis: {
        categories: [
          "2016",
          "2017",
          "2018",
          "2019",
          "2020",
          "2021",
        ]
      },
      yaxis: {
        min: 10,
        max: 200,
        title: {
          text: "Income Report"
        }
      },
      legend: {
        position: "top",
        horizontalAlign: "right",
        floating: true,
        offsetY: -25,
        offsetX: -5
      },
      fill: {
        opacity: 1
      },
      tooltip: {
        y: {
          formatter: function(val) {
            return "$ " + val + " thousands";
          }
        }
      }
    }

    var chartBar = new ApexCharts(document.querySelector("#chartBar"), optionsChartBar);

    setTimeout(function() { chartBar.render(); }, 300);
  }
  // chartBar activation end


  // chartPie activation start
  if (jQuery("#chartPie").length > 0) {
    var optionsChartPie = {
        series: [45, 30, 25],
      chart: {
        width: 380,
        type: "donut"
      },
      labels: ["Income", "Expense", "Balance"],
      dataLabels: {
        enabled: false
      },
      fill: {
        type: "gradient"
      },
      title: {
        text: "Piechart Report",
        align: "left",
      },
      colors: ["#6F4EF6", "#5BC5A8", "#FF9720"],
      responsive: [
        {
          breakpoint: 1600,
          options: {
            chart: {
              width: 315
            }
          }
        },
        {
          breakpoint: 1200,
          options: {
            chart: {
              width: 400
            }
          }
        },
        {
          breakpoint: 575,
          options: {
            chart: {
              width: 300,
              height: 250
            },
            legend: {
              position: "bottom"
            }
          }
        }
      ]
    }

    var chartPie = new ApexCharts(document.querySelector("#chartPie"), optionsChartPie);

    setTimeout(function() { chartPie.render(); }, 300);
  }
  // chartPie activation end

  // incomeChart activation start
  if (jQuery("#incomeChart").length > 0) {
    var optionsIncomeChart = {
        series: [
          {
            name: "Net Profit",
            data: [44, 55, 57, 56, 61, 58, 63, 60, 66, 52, 75, 85]
          }
        ],
        chart: {
          type: "bar",
          height: 80,
          width: 380
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: "55%",
            endingShape: "rounded"
          }
        },
        dataLabels: {
          enabled: false
        },
        xaxis: {
          categories: [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec"
          ]
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
            formatter: function(val) {
              return "$ " + val + " thousands";
            }
          }
        }
    }

    var incomeChart = new ApexCharts(document.querySelector("#incomeChart"), optionsIncomeChart);

    setTimeout(function() { incomeChart.render(); }, 300);
  }
  // incomeChart activation end


  // shortmenu Js start
  $("#shortmenu").on("click", function () {
    $(".cashier-quick-menu-dropdown").toggleClass("shortmenu-enable");
    $(".cashier-header-overlay").toggleClass("shortmenu-enable");
    $(".cashier-quick-lang-dropdown").removeClass("langmenu-enable");
    $(".cashier-notification-dropdown").removeClass("notifydropdown-enable");
    $(".cashier-email-dropdown").removeClass("emaildropdown-enable");
  });
  $(".cashier-header-overlay").on("click", function () {
    $(".cashier-quick-menu-dropdown").removeClass("shortmenu-enable");
    $(".cashier-header-overlay").removeClass("shortmenu-enable");
  });
  // shortmenu Js end

  // langdropdown Js start
  $("#langdropdown").on("click", function () {
    $(".cashier-quick-lang-dropdown").toggleClass("langmenu-enable");
    $(".cashier-header-overlay").toggleClass("langmenu-enable");
    $(".cashier-quick-menu-dropdown").removeClass("shortmenu-enable");
    $(".cashier-notification-dropdown").removeClass("notifydropdown-enable");
    $(".cashier-email-dropdown").removeClass("emaildropdown-enable");
  });
  $(".cashier-header-overlay").on("click", function () {
    $(".cashier-quick-lang-dropdown").removeClass("langmenu-enable");
    $(".cashier-header-overlay").removeClass("langmenu-enable");
  });
  // langdropdown Js end

  // notifydropdown Js start
  $("#notifydropdown").on("click", function () {
    $(".cashier-notification-dropdown").toggleClass("notifydropdown-enable");
    $(".cashier-header-overlay").toggleClass("notifydropdown-enable");
    $(".cashier-quick-menu-dropdown").removeClass("shortmenu-enable");
    $(".cashier-quick-lang-dropdown").removeClass("langmenu-enable");
    $(".cashier-email-dropdown").removeClass("emaildropdown-enable");
  });
  $(".cashier-header-overlay").on("click", function () {
    $(".cashier-notification-dropdown").removeClass("notifydropdown-enable");
    $(".cashier-header-overlay").removeClass("notifydropdown-enable");
  });
  // notifydropdown Js end
  
  // emaildropdown Js start
  $("#emaildropdown").on("click", function () {
    $(".cashier-email-dropdown").toggleClass("emaildropdown-enable");
    $(".cashier-header-overlay").toggleClass("emaildropdown-enable");
    $(".cashier-quick-menu-dropdown").removeClass("shortmenu-enable");
    $(".cashier-quick-lang-dropdown").removeClass("langmenu-enable");
    $(".cashier-notification-dropdown").removeClass("notifydropdown-enable");
  });
  $(".cashier-header-overlay").on("click", function () {
    $(".cashier-email-dropdown").removeClass("emaildropdown-enable");
    $(".cashier-header-overlay").removeClass("emaildropdown-enable");
  });
  // emaildropdown Js end

  // sidebarToggle js start
  $("#sidebarToggle").on("click", function() {
    $(".cashier-dashboard-sidebar").toggleClass("sidebar-enable");
    $(".cashier-dashboard-main").toggleClass("sidebar-enable");
    $(".cashier-menu-overlay").toggleClass("sidebar-enable");
  });
  $(".cashier-menu-overlay").on("click", function () {
    $(".cashier-dashboard-sidebar").removeClass("sidebar-enable");
    $(".cashier-dashboard-main").removeClass("sidebar-enable");
    $(".cashier-menu-overlay").removeClass("sidebar-enable");
  });
  // sidebarToggle js end

  // password show hide start 
  $(".toggle-password").click(function () {
    
    $(this).toggleClass("fa-eye fa-eye-slash");
    var input = $($(this).attr("formaction"));
    if (input.attr("type") == "password") {
      input.attr("type", "text");
    } else {
      input.attr("type", "password");
    }
  });
  // password show hide end


  // dropdown action start 
    $(".dropdown").click(function(){
      $(this).find(".dropdown-list").fadeToggle(100);
    });
  $(document).on("click", function(event){
    var $trigger = $(".dropdown");
    if($trigger !== event.target && !$trigger.has(event.target).length){
      $(".dropdown-list").fadeOut(100);
    }
  });
  // dropdown action end 

  // popup action start 
  $(".open").click(function (){
    $(".pop-outer").fadeIn("slow");
  });
  $(".close").click(function (){
      $(".pop-outer").fadeOut("slow");
  });
  $(".openA").click(function (){
    $(".pop-outerA").fadeIn("slow");
  });
  $(".closeA").click(function (){
      $(".pop-outerA").fadeOut("slow");
  });
  $(".openB").click(function (){
    $(".pop-outerB").fadeIn("slow");
  });
  $(".closeB").click(function (){
      $(".pop-outerB").fadeOut("slow");
  });
  // popup action end

  // custom tab action start 
  $(document).ready(function () {
    $('.tab-a').click(function () {
      $(".tab").removeClass('tab-active');
      $(".tab[data-id='" + $(this).attr('data-id') + "']").addClass("tab-active");
      $(".tab-a").removeClass('active-a');
      $(this).parent().find(".tab-a").addClass('active-a');
    });
  });
  $(document).ready(function () {
    $('.tab-b').click(function () {
      $(".tab").removeClass('tab-activeA');
      $(".tab[data-id='" + $(this).attr('data-id') + "']").addClass("tab-activeA");
      $(".tab-b").removeClass('active-b');
      $(this).parent().find(".tab-b").addClass('active-b');
    });
  });
  // custom tab action end 

  $(document).ready(function(){

  $(':checkbox.selectall').on('click', function(){
    $(':checkbox[name=' + $(this).data('checkbox-name') + ']').prop("checked", $(this).prop("checked"));
  });
  // Individual checkboxes
  $(':checkbox.checkme').on('click', function(){ // 1

    var _this = $(this); // 2
    var _selectall = _this.prop("checked"); //3

    if ( _selectall ) { // 4
      // 5
      $( ':checkbox[name=' + _this.attr('name') + ']' ).each(function(i){
        // 6
        _selectall = $(this).prop("checked");
        return _selectall; // 7
      });

    }

    // 8
    $(':checkbox[name=' + $(this).data('select-all') + ']').prop("checked", _selectall);
  });

});


})(jQuery);