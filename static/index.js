function change_links (target_links){
  var links_list = $('#target-links')
  links_list.empty();

  var num = target_links.length;
  for(var i = 0; i < num; i++) {
      var text = $('<h4/>').html(target_links[i][0] + "'s Segment")
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




function page_update(url){
  var frame = parseInt($('#alert-img').attr("frame-num"));
  var video = $("#video-selection").val().slice(13);


    $.ajax({
        url: url,
        data:  {"frame":frame, "video":video},
        type: 'GET',
        success: function(response) {
          //console.log(response);
            var img = new Image();
            img.src = response["img_url"];
            img.onload = function(){
 $("#alert-img").attr("src", img.src);
 $("#alert-img").attr("frame-num", response["frame_num"]);
 //console.log(response);
}
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
    timeout = setInterval(function(){page_update("/next");}, 100);

}

function rewind(){
    timeout = setInterval(function(){page_update("/previous");}, 100);

}



timeout = 0;

$(function() {

    $('#next-button').click(next_update);
    $('#previous-button').click(previous_update);
    $('#play-button').click(play);
    $('#rewind-button').click(rewind);
    $('#stop-button').click(function(){clearInterval(timeout);})


})
