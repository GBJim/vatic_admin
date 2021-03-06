function change_links (target_links){
  var links_list = $('#target-links')
  links_list.empty();

  var num = target_links.length;
  for(var i = 0; i < num; i++) {
      var span = $('<span/>').attr("class", "glyphicon glyphicon-hand-right");
      var text = $('<h4/>').html(target_links[i][0] + "'s Segment  " ).append(span);
      var link = $('<a/>').attr('href', target_links[i][1]).append(text);
      var item = $('<li/>').attr('class', "list-group-item").append(link);
      links_list.append(item);
}



}

function update_wrong_number(alert){
  var w_list = $("#w-list");
  w_list.empty();
  if("wrong_number" in alert){

    for(var user in alert["wrong_number"]) {
        var span = $('<span/>').attr("class", "badge").html(alert["wrong_number"][user]);
        var item = $('<li/>').attr('class', "list-group-item").append(span).append(user);
        w_list.append(item);
        }
  }

}









function update_isolation(alert){

  var i_list = $("#i-list");
  i_list.empty();
  if("isolation" in alert){

    for(var user in alert["isolation"]) {
        var span = $('<span/>').attr("class", "badge").html(Object.keys(alert["isolation"][user]).length);
        var item = $('<li/>').attr('class', "list-group-item").append(span).append(user);
        i_list.append(item);
        }
  }

  }











function update_alert(alert){
  update_wrong_number(alert);
  update_isolation(alert);
}





function page_update_seek(frame){

  var video = $("#video-selection").val().slice(13);


    $.ajax({
        url: "/seek",
        data:  {"frame":frame, "video":video},
        type: 'GET',
        success: function(response) {


          //console.log(response);
          render_image(frame, video);

 $("#frame-num").html(response["frame_num"]);

 update_alert(response["alert"]);
 change_links(response["target_links"]);

        },
        error: function(error) {
            console.log(error);

        }
    });


}




function page_update(url){
  var frame = $("#frame-num").html();

  var video = $("#video-selection").val().slice(13);


    $.ajax({
        url: url,

        data:  {"frame":frame, "video":video},
        type: 'GET',
        success: function(response) {
          console.log(response);

          render_image(response["frame_num"], video);

 $("#frame-num").html(response["frame_num"]);
 update_alert(response["alert"]);
 change_links(response["target_links"]);

        },
        error: function(error) {
            console.log(error);

        }
    });


}

function next_update(){

  page_update("/next");
}




function previous_update(){
  page_update("/previous");


}

function play(){
    clearInterval(rewind_ID);
    if (play_ID == 0){
    play_ID  = setInterval(function(){page_update("/next");}, 100);
  }
}

function rewind(){
    clearInterval(play_ID);
    if (rewind_ID == 0){
    rewind_ID = setInterval(function(){page_update("/previous");}, 100);
  }
}

function stop(){
    clearInterval(play_ID);
    clearInterval(rewind_ID);
    play_ID = 0;
    rewind_ID = 0;


}



play_ID = 0;
rewind_ID = 0;


function check_fire(error_data){

  console.log(error_data);
  $.ajax({
     url: "/box_check",
     type: 'GET',
     data: error_data
           });

}



function box_events(){
  /*
  video = $(this).data("video");
  master = $(this).data("master");
  reference = $(this).data("reference");
  type = $(this).data("type");
  begin = $(this).data("begin");
  end = $(this).data("end");
  box_id = $(this).data("id");


  error_data = {"video":video, "master":master, "reference": reference,"box_id":box_id, "type":type, "begin":begin,"end":end}
  */
  error_id = $(this).data("error");
  error_data = {"id": error_id};



  if($(this).is(":checked")){
    error_data["action"] = "insert"
    check_fire(error_data);
  }
  else {
    error_data["action"] = "remove"
    check_fire(error_data);

  }
}






function render_boxes(boxes, svg){







           d3.selectAll("g.box").remove();
           var num = boxes.length;
           for(var i = 0; i < num; i++) {
             var box = boxes[i];

             var box_group = svg.append("g").attr("class", "box").attr("id", box["source"] + "-" + box["id"]);



             box_group.append("rect")
             .attr("x", box['xmin'])
             .attr("y", box['ymin'])
             .attr("width", box['xmax'] - box['xmin'])
             .attr("height", box['ymax'] - box['ymin'])
             .style("stroke",color_map[box["source"]])
             .style("stroke-width",3)
             .style("fill", "none");



             box_group.append("rect")
                .attr("x", box['xmin']-2)
                .attr("y", box['ymin'] - 17)
                .attr("width", 7.5*(box["source"] + "-" + box["id"]).length + 0.5)
                .attr("height", 15)
                .attr("fill", color_map[box["source"]])
                .style("opacity", 0.6);


             box_group.append("text")
                .attr("x", box['xmin'])
                .attr("y", box['ymin'] - 5)
                .text(box["source"] + "-" + box["id"])
                .attr("font-size", "14px")
                .attr("fill", "white");





             }




}




function highlight_box(box_id){
  d3.selectAll(".box").style("opacity", 0);
  d3.select("#"+box_id).style("opacity",1);
  console.log(box_id);

}


function show_all_box(box_id){
  d3.selectAll(".box").style("opacity", 1);


}




function get_color_map(){
  var color_map = {};
  var meta_tags = $("meta");
  var num = meta_tags.length;
  for (i=0; i<num; i++){
    color_map[meta_tags[i].name] = meta_tags[i].content;

  }
  return color_map





}




function render_image(frame, video){





    var params = { frame:frame, video:video };
    var img_url = "/image?" + jQuery.param(params);
    console.log(img_url)
      var svg = d3.select("#alert-svg");

      svg.append("image")
      .attr("xlink:href", img_url)
      .attr("x", "0")
      .attr("y", "0");



       $.ajax({
           url:"/alert_boxes" ,
           data:  {"frame":frame, "video":video},
           type: 'GET',
           success: function(response) {
             //console.log(response);

             render_boxes(response, svg)

           },
           error: function(error) {
               console.log(error);

           }
       });
     }


$(function() {
    color_map = get_color_map();

    $('#next-button').click(next_update);
    $('#previous-button').click(previous_update);
    $('#play-button').click(play);
    $('#rewind-button').click(rewind);
    $('#stop-button').click(stop)
    $("input:checkbox").change(box_events);

    var frame = parseInt($('#alert-svg').attr("frame-num"));
    var video = $("#video-selection").val().slice(13);




    render_image(frame, video);


    $("tr").not(':first').hover(
  function () {
  console.log(this.getAttribute("box-id"));
  highlight_box(this.getAttribute("box-id"));
  },
  function () {
    show_all_box();
  }
);










})
