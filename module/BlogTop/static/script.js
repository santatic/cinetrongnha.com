var PageModuleBlogTop=function(a){this.app=a;this.setting={"class":{},trigger:{},"max-height":0,user:!0,blank:!1,view:!0,like:!0,share:!0,comment:!0,more:!0,"new-page":!1,"view-inline":0};this.template={};this.view_inlined=0;this.view_inlining=!1};
PageModuleBlogTop.prototype={Description:function(){return"this.descript"},Init:function(a){if("undefined"==typeof this.inited)this.inited=!0;else return!0;var c=this;this.form=a;this.posts=this.form.find(".main .posts:first");a=JSON.parse(Base64.decode(this.form.attr("module-setting")));for(var b in a)this.setting[b]=a[b];c.template.post=Base64.decode(c.form.attr("module-template"));this.form.bind("more",function(a,b){c.form.find(".footer .view-more").click();a.preventDefault()});c.app._Router.AddCallback(this.form.parents("[site-name]:first").attr("site-name"),
this.form.parents("[page-name]:first").attr("page-name"),function(a){a=a.match(/[a-z0-9]{24}/g);null!=a&&0<a.length&&(a=a[0],c.form.find(".post").removeClass("active"),c.form.find(".post[post-id="+a+"]").addClass("active"))})},Load:function(a,c){var b=this;b.view_inlining=!0;if("undefined"!=typeof a.post){"string"==typeof a.time&&$.each(b.form.find(".main .post"),function(b,c){var f=$(c),e=f.find(".time:first").attr("time");a.time>=e&&(a.post.push(f.attr("post-id")),a.time=e)});"string"==typeof a.view&&
$.each(b.form.find(".main .post"),function(b,c){var e=$(c);e.find(".view .value:first").html()==a.view&&a.post.push(e.attr("post-id"))});var e=[];$.each(a.post,function(a,b){-1===$.inArray(b,e)&&e.push(b)});a.post=e.join(",")}a.module=b.form.attr("module-id");b.app._ProcessBar.Reset();b.app._ProcessBar.Run(50);PageAjax({url:window.location.href,type:"post",dataType:"json",data:a}).done(function(a){b.view_inlining=!1;"undefined"!=typeof a.post&&(b.app._ProcessBar.Run(100),"overwrite"==c&&b.posts.children().remove(),
"object"==typeof a.post&&0<a.post.length&&(b.posts.append(b.Render("post",a.post)),b.Refesh()))}).error(function(a){b.view_inlining=!1;console.error(a)})},Render:function(a,c){var b=this,e="";$.each(c,function(c,g){var f=b.template[a];$.each(g,function(a,b){f=f.split("{{ "+a+" }}").join(b)});e+=f});return e},Refesh:function(){var a=this;"undefined"!=typeof a.setting["class"]&&$.each(a.setting["class"],function(b,c){var d=a.form.find("."+b);$.each(d,function(a,b){var d=$(b);d.data("md-classed")||d.addClass(c).data("md-classed",
!0)})});var c=a.form.find(".content .video");$.each(c,function(a,b){var d=$(b),c=d.attr("link");try{var c=c.split("youtube.com/watch?v=",2)[1].split("/[#|?]/",1)[0],e=$('<img class="picture" src="http://i1.ytimg.com/vi/'+c+'/hqdefault.jpg"></img>').insertAfter(d),f=$('<div class="play-button"></div>').insertAfter(e);d.remove();f.css({top:(.7*e.width()-35)/2,left:(e.width()-50)/2})}catch(g){console.error(g)}});"undefined"==typeof a.setting.trigger||"undefined"==typeof a.setting.trigger.more||a.form.data("md-more-trigged")||
(a.form.on("click",".footer .view-more",function(b){$.each(a.setting.trigger.more,function(b,d){a.form.parents(".page:first").find("[module-id="+d+"]:first").trigger("more","more")});b.preventDefault()}),a.form.data("md-more-trigged",!0));if("undefined"!=typeof a.setting.user){var b=a.form.find(".post .user .by");a.setting.user?b.show():b.hide()}"undefined"!=typeof a.setting.blank&&a.setting.blank?(c=a.form.find(".posts .post"),$.each(c,function(a,b){var d=$(b);d.data("md-blanked")||(d.find(".content a").attr("target",
"_blank"),d.find(".title a").attr("target","_blank"),d.data("md-blanked",!0))})):a.form.find(".post .content a:not([site-goto]), .post .title a:not([site-goto])").attr("site-goto","");"undefined"!=typeof a.setting.like&&a.setting.like&&(b=a.form.find(".post .user .info .like").show(),$.each(b,function(a,b){var d=$(b);if(!d.data("md-liked")){var c=d.parents(".post:first").find(".title a:first")[0].href;if(0==d.children().length){$('<div class="fb-like " data-width="'+d.width()+'px" data-href="'+c+
'" data-layout="button_count" data-action="like" data-show-faces="false" data-share="false"></div>').appendTo(d);try{FB.XFBML.parse(this)}catch(e){console.debug(e)}}d.data("md-liked",!0)}}));c=!1;"undefined"!=typeof a.setting.view&&a.setting.view&&a.form.find(".post .user .info .view").show();"undefined"!=typeof a.setting.share&&a.setting.share&&(a.form.find(".post .user .info .share").show(),c=!0);"undefined"!=typeof a.setting.comment&&a.setting.comment&&(a.form.find(".post .user .info .comment").show(),
c=!0);c&&(c=a.form.find(".posts .post"),$.each(c,function(a,b){var d=$(b);if(!d.data("md-fb-info-updated")){var c=d.find(".title a:first")[0].href;$.getJSON("http://graph.facebook.com/?id="+c,function(a){d.find(".info .comment:first").append("undefined"!=typeof a.comments?a.comments:0);d.find(".info .share:first").append("undefined"!=typeof a.shares?a.shares:0)});d.data("md-fb-info-updated",!0)}}));"undefined"!=typeof a.setting.more&&(c=a.form.find(".footer .view-more"),c.data("md-mored")||(a.setting.more?
c.show():c.hide(),c.data("md-mored",!0)));if("undefined"!=typeof a.setting["new-page"]&&a.setting["new-page"]){if(c=a.form.find(".footer .view-more:visible"),0<c.length){var b=a.form.find(".main .post:last"),e=b.find(".time:first").attr("time"),k=[b.attr("post-id")],b=b.find(".view .value:first").html();c.attr("site-goto","");c.attr("href","?time="+e+"&post="+k+"&view="+b);a.form.data("md-view-more-callbacked")||(a.app._Router.AddCallback(a.form.parents("[site-name]:first").attr("site-name"),a.form.parents("[page-name]:first").attr("page-name"),
function(b){var c={};try{b=b.split("?",2);if(2==b.length){b=b[1].split("#",1)[0];b=b.split("&");for(var d in b)d=b[d],d=d.split("=",2),"post"==d[0]?c.post=[d[1]]:"time"==d[0]?c.time=d[1]:"view"==d[0]&&(c.view=d[1])}a.Load(c,"overwrite")}catch(e){console.error(e)}}),a.form.data("md-view-more-callbacked",!0))}}else a.form.data("md-view-mored")||(a.form.on("click",".view-more",function(b){var c=a.form.find(".main .post:last");if(1==c.length){var d=c.find(".time:first").attr("time"),e=[c.attr("post-id")],
c=c.find(".view .value:first").html();a.Load({time:d,post:e,view:c})}b.preventDefault()}),a.form.data("md-view-mored",!0));"number"==typeof a.setting["max-height"]&&(b=a.form.find(".main:first"),b.data("md-heighted")||(0<a.setting["max-height"]?b.css("max-height",a.setting["max-height"]+"vh"):0>a.setting["max-height"]&&b.css("max-height","none"),b.data("md-heighted",!0)));if(0<a.setting["view-inline"]){var g=a.form.offset().top-($(window).height()+100),f=function(b){a.view_inlined=0},h=function(){if(a.form.is(":visible")){var b=
a.form.height()+g;if($(this).scrollTop()>=b&&!a.view_inlining&&a.view_inlined<a.setting["view-inline"]){a.view_inlined++;var c=a.form.find(".main .post:last");if(1==c.length){var b=c.find(".time:first").attr("time"),d=[c.attr("post-id")],c=c.find(".view .value:first").html();a.Load({time:b,post:d,view:c})}}}else $(window).unbind("scroll",h),a.form.off("click",".view-more",f)};$(window).scroll(h);a.form.on("click",".view-more",f)}this.timer=this.form.find(".user .info .time:first");this.timer.data("timer")||
(a.app._Timer.Add(a.timer),a.timer.data("timer",!0))}};
