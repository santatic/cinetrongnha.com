var PageModuleBlogManager=function(b){this.app=b;this.setting={"class":{},trigger:{},height:0,user:!0,blank:!1,view:!0,like:!0,share:!0,comment:!0,more:!0};this.template={}};
PageModuleBlogManager.prototype={Description:function(){return"this.descript"},Init:function(b){if("undefined"==typeof this.inited)this.inited=!0;else return!0;var a=this;this.form=b;this.posts=this.form.find(".main .posts:first");b=JSON.parse(Base64.decode(this.form.attr("module-setting")));for(var e in b)this.setting[e]=b[e];a.template.post=Base64.decode(a.form.attr("module-template"));this.form.on("click",".view-more",function(c){var d=a.form.find(".main .post:last");if(1==d.length){var b=d.find(".time:first").attr("time"),
f=[d.attr("post-id")],d=d.find(".view .value:first").html();a.Load(window.location.href,{time:b,post:f,view:d})}c.preventDefault()});this.form.on("click",".post .manager>.btn.public",function(c){var d=$(this);d.attr("disabled","disabled");var b=(new Date).toLocaleString();a.modal_title.html("Public post");a.modal_body.html('<div class="input-group">\t\t\t\t\t\t\t\t\t<input type="datetime" value="'+b+'" class="timer form-control">\t\t\t\t\t\t\t\t\t<span class="input-group-btn">\t\t\t\t\t\t\t\t\t\t<button class="btn btn-default reset" type="button"><span class="glyphicon glyphicon-repeat"></span></button>\t\t\t\t\t\t\t\t\t</span>\t\t\t\t\t\t\t\t</div>');
a.modal_footer.html('<button type="button" class="btn btn-primary btn-public">Public</button>\t\t\t\t\t\t\t\t\t<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');a.modal_object=d.parents(".post:first");a.modal.modal("show");c.preventDefault();c.stopPropagation()});this.form.on("click",".post .manager>.btn.private",function(c){var d=$(this);d.attr("disabled","disabled");a.ManagerPost(d.parents(".post:first"),{is:"private"});c.preventDefault();c.stopPropagation()});
this.form.on("click",".post .manager>.btn.trash",function(c){var d=$(this);d.attr("disabled","disabled");a.modal_title.html("Trash post");a.modal_body.html("Move this post to trash ?");a.modal_footer.html('<button type="button" class="btn btn-danger btn-trash" data-dismiss="modal">Trash</button>\t\t\t\t\t\t\t\t\t<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');a.modal_object=d.parents(".post:first");a.modal.modal("show");c.preventDefault();c.stopPropagation()});
this.form.on("click",".post .manager>.btn.restore",function(c){var d=$(this);d.attr("disabled","disabled");a.modal_title.html("Restore post");a.modal_body.html("Restore this post to private box?");a.modal_footer.html('<button type="button" class="btn btn-success btn-restore" data-dismiss="modal">Restore</button>\t\t\t\t\t\t\t\t\t<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');a.modal_object=d.parents(".post:first");a.modal.modal("show");c.preventDefault();
c.stopPropagation()});this.form.on("click",".post .manager>.btn.edit",function(c){var d=$(this);d.attr("disabled","disabled");var b=d.parents(".post:first");query={action:"edit"};query.module=a.form.attr("module-id");query.post=b.attr("post-id");a.app._ProcessBar.Reset();a.app._ProcessBar.Run(50);PageAjax({type:"post",dataType:"json",url:window.location.href,data:query}).done(function(c){console.debug(c);a.app._ProcessBar.Run(100);"undefined"!=typeof c.post&&(a.modal_title.html("Edit post"),a.modal_body.html('<label>Ti\u00eau \u0111\u1ec1 c\u1ee7a b\u00e0i vi\u1ebft</label><input type="text" name="title" class="form-control" placeholder="Ti\u00eau \u0111\u1ec1">\t\t\t\t\t\t\t\t\t\t<label>Tin nh\u1eafn</label><textarea class="form-control" name="note" placeholder="Tin nh\u1eafn" rows="3"></textarea>\t\t\t\t\t\t\t\t\t\t<label>Ngu\u1ed3n</label><input type="text" name="source" class="form-control" placeholder="Ngu\u1ed3n">\t\t\t\t\t\t\t\t\t\t<label><input type="checkbox" name="safekid"> N\u1ed9i dung nh\u1ea1y c\u1ea3m</label>'),
a.modal_body.find("[name=title]:first").val(c.post.title),a.modal_body.find("[name=note]:first").val(c.post.note),a.modal_body.find("[name=source]:first").val(c.post.source),1==c.post.safekid&&a.modal_body.find("[name=safekid]:first").attr("checked","checked"),a.modal_footer.html('<button type="button" class="btn btn-warning btn-edit" data-dismiss="modal">Edit</button>\t\t\t\t\t\t\t\t\t\t\t<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>'),a.modal_object=
b,a.modal.modal("show"))}).error(function(a){console.error(a)});c.preventDefault();c.stopPropagation()});this.form.on("click",".post .manager>.btn.delete",function(c){var d=$(this);d.attr("disabled","disabled");a.modal_title.html("Restore post");a.modal_body.html("Delete this box?");a.modal_footer.html('<button type="button" class="btn btn-danger btn-delete" data-dismiss="modal">Delete</button>\t\t\t\t\t\t\t\t\t<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');
a.modal_object=d.parents(".post:first");a.modal.modal("show");c.preventDefault();c.stopPropagation()});a.app._Router.AddCallback(this.form.parents("[site-name]:first").attr("site-name"),this.form.parents("[page-name]:first").attr("page-name"),function(c){var d=c.match(/[a-z0-9]{24}/g);null!=d&&0<d.length&&(d=d[0],a.form.find(".post").removeClass("active"),a.form.find(".post[post-id="+d+"]").addClass("active"));try{var b=c.split("?",2)[1].split("&"),f;for(f in b)if(l=b[f].split("="),"tab"==l[0])var e=
l[1]}catch(h){}"undefined"!=typeof e&&(b=a.form.find(".tabmenu:first>li[md-tab="+e+"]"),b.length=!b.hasClass("active"))&&(f=a.form.find(".tabmenu:first>li.active"),a.form.find(".tabmenu:first>li").removeClass("active"),b.addClass("active"),b=f.attr("md-tab"),a.form.find(".posts:first .post").remove(),a.Load(c,{}),a.form.find(".posts:first").removeClass(b).addClass(e))});this.modal=$('<div class="modal fade"role="dialog" aria-hidden="true">\t\t\t\t\t\t\t<div class="modal-dialog">\t\t\t\t\t\t\t\t<div class="modal-content">\t\t\t\t\t\t\t\t\t<div class="modal-header">\t\t\t\t\t\t\t\t\t\t<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>\t\t\t\t\t\t\t\t\t\t<h4 class="modal-title"></h4>\t\t\t\t\t\t\t\t\t</div>\t\t\t\t\t\t\t\t\t<div class="modal-body"></div>\t\t\t\t\t\t\t\t\t<div class="modal-footer"></div>\t\t\t\t\t\t\t\t</div>\t\t\t\t\t\t\t</div>\t\t\t\t\t\t</div>').modal({show:!1});
this.modal_title=this.modal.find(".modal-title:first");this.modal_body=this.modal.find(".modal-body:first");this.modal_footer=this.modal.find(".modal-footer:first");this.modal.on("hidden.bs.modal",function(c){a.form.find(".manager .btn").removeAttr("disabled")});this.modal.on("click",".modal-footer .btn.btn-public",function(c){c=$(this).parents(".modal:first").find(".timer:first").val();c=(new Date(c)).getTime();c-=(new Date).getTime();isNaN(c)||(a.modal.modal("hide"),a.ManagerPost(a.modal_object,
{is:"public",timestep:c}))});this.modal_body.on("click",".btn.reset",function(a){a=(new Date).toLocaleString();$(this).parents(".modal:first").find(".timer:first").val(a)});this.modal.on("click",".modal-footer .btn.btn-trash",function(c){a.ManagerPost(a.modal_object,{is:"trash"})});this.modal.on("click",".modal-footer .btn.btn-restore",function(c){a.ManagerPost(a.modal_object,{is:"restore"})});this.modal.on("click",".modal-footer .btn.btn-edit",function(c){c={is:"edit"};c.p_title=a.modal_body.find("[name=title]:first").val();
c.p_note=a.modal_body.find("[name=note]:first").val();c.p_source=a.modal_body.find("[name=source]:first").val();c.p_safekid=a.modal_body.find("[name=safekid]:first").is(":checked");a.ManagerPost(a.modal_object,c)});this.modal.on("click",".modal-footer .btn.btn-delete",function(c){a.ManagerPost(a.modal_object,{is:"delete"})})},Load:function(b,a){var e=this;if("undefined"!=typeof a.post){"string"==typeof a.time&&$.each(e.form.find(".main .post"),function(c,b){var f=$(b);f.find(".time:first").attr("time")==
a.time&&a.post.push(f.attr("post-id"))});"string"==typeof a.view&&$.each(e.form.find(".main .post"),function(c,b){var f=$(b);f.find(".view .value:first").html()==a.view&&a.post.push(f.attr("post-id"))});var c=[];$.each(a.post,function(a,b){-1===$.inArray(b,c)&&c.push(b)});a.post=c.join(",")}a.module=e.form.attr("module-id");e.app._ProcessBar.Reset();e.app._ProcessBar.Run(50);PageAjax({type:"post",dataType:"json",url:b,data:a}).done(function(a){"undefined"!=typeof a.post&&(e.app._ProcessBar.Run(100),
e.posts.append(e.Render("post",a.post)),e.Refesh())}).error(function(a){console.error(a)})},ManagerPost:function(b,a){var e=this;a.action="manager";a.module=e.form.attr("module-id");a.post=b.attr("post-id");e.app._ProcessBar.Reset();e.app._ProcessBar.Run(50);PageAjax({type:"post",dataType:"json",url:window.location.href,data:a}).done(function(c){e.app._ProcessBar.Run(100);if(0==c.error)if(c=b.find(".manager"),"trash"==a.is||"restore"==a.is||"delete"==a.is)b.remove();else if("public"==a.is||"private"==
a.is)c.children().removeAttr("disabled"),c.removeClass("public private").addClass(a.is)}).error(function(a){console.error(a)})},Render:function(b,a){var e=this,c="";$.each(a,function(a,g){var f=e.template[b];$.each(g,function(a,b){f=f.split("{{ "+a+" }}").join(b)});c+=f});return c},Refesh:function(){var b=this;"undefined"!=typeof b.setting["class"]&&$.each(b.setting["class"],function(a,c){var d=b.form.find("."+a);$.each(d,function(a,b){var d=$(b);d.data("md-classed")||d.addClass(c).data("md-classed",
!0)})});var a=b.form.find(".content .video");$.each(a,function(a,b){var d=$(b),g=d.attr("link");try{var g=g.split("youtube.com/watch?v=",2)[1].split("/[#|?]/",1)[0],f=$('<img class="picture" src="http://i1.ytimg.com/vi/'+g+'/hqdefault.jpg"></img>').insertAfter(d),k=$('<div class="play-button"></div>').insertAfter(f);d.remove();k.css({top:(.7*f.width()-35)/2,left:(f.width()-50)/2})}catch(h){console.error(h)}});"undefined"!=typeof b.setting.user&&(a=b.form.find(".post .user .by"),b.setting.user?a.show():
a.hide());"undefined"!=typeof b.setting.blank&&b.setting.blank?(a=b.form.find(".posts .post"),$.each(a,function(a,b){var d=$(b);d.data("md-blanked")||(d.find(".image a").attr("target","_blank"),d.find(".title a").attr("target","_blank"),d.data("md-blanked",!0))})):b.form.find(".post .image a:not([site-goto]), .post .title a:not([site-goto])").attr("site-goto","+");a=!1;"undefined"!=typeof b.setting.view&&b.setting.view&&b.form.find(".post .user .info .view").show();"undefined"!=typeof b.setting.like&&
b.setting.like&&(b.form.find(".post .user .info .like").show(),a=!0);"undefined"!=typeof b.setting.share&&b.setting.share&&(b.form.find(".post .user .info .share").show(),a=!0);"undefined"!=typeof b.setting.comment&&b.setting.comment&&(b.form.find(".post .user .info .comment").show(),a=!0);a&&(a=b.form.find(".posts .post"),$.each(a,function(a,b){var d=$(b);if(!d.data("md-fb-info-updated")){var g=d.find(".title a:first")[0].href;$.getJSON("http://graph.facebook.com/?id="+g,function(a){d.find(".info .like:first").append("undefined"!=
typeof a.likes?a.likes:0);d.find(".info .comment:first").append("undefined"!=typeof a.comments?a.comments:0);d.find(".info .share:first").append("undefined"!=typeof a.shares?a.shares:0)});d.data("md-fb-info-updated",!0)}}));"undefined"!=typeof b.setting.more&&(a=b.form.find(".footer .view-more"),a.data("md-mored")||(b.setting.more?a.show():a.hide(),a.data("md-mored",!0)));"number"==typeof b.setting["max-height"]&&0<b.setting["max-height"]&&(a=b.form.find(".main:first"),a.data("md-heighted")||(a.css("max-height",
b.setting["max-height"]+"vh"),a.data("md-heighted",!0)));this.timer=this.form.find(".user .info .time:first");this.timer.data("timer")||(b.app._Timer.Add(b.timer),b.timer.data("timer",!0))}};