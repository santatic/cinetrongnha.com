
// var PageModuleCineManager = function(app){
// 	this.app 		= app;
// 	this.setting 	= {
// 		"class": 	{},
// 		"trigger": 	{},
// 		"height": 	0,
// 		"user": 	true,
// 		"blank": 	false,
// 		"view": 	true,
// 		"like": 	true,
// 		"share": 	true,
// 		"comment": 	true,
// 		"more": 	true
// 	};
// 	this.template 	= {};
// 	// this.store 		= {};
// };

// PageModuleCineManager.prototype = {
// 	Description: function(){
// 		// this.descript = $('<h3>module PageModuleCineManager</3></h4>module duoc dung de show cac bai post, anh, duong dan den cac bai post ...</h4>');
// 		return "this.descript";
// 	},
// 	Init: function(form){
// 		if (typeof(this.inited) == "undefined") {
// 			this.inited 	= true;
// 		}else{
// 			return true;
// 		};

// 		var self 		= this;
// 		this.form 		= form;
// 		this.posts 		= this.form.find('.main .posts:first');
// 		// setting
// 		var setting 	= JSON.parse(Base64.decode(this.form.attr('module-setting')))
// 		for(var set in setting){
// 			this.setting[set] = setting[set];
// 		}
// 		// load template of post
// 		self.template['post'] = Base64.decode(self.form.attr('module-template'));

// 		this.form.on('click', '.view-more', function(event){
// 			var obj 	= self.form.find('.main .post:last');
// 			if (obj.length == 1) {
// 				var time 	= obj.find('.time:first').attr('time');
// 				var post 	= [obj.attr('post-id')];
// 				var view 	= obj.find('.view .value:first').html();
// 				self.Load(
// 					window.location.href,
// 					{
// 						"time": time,
// 						"post": post,
// 						"view": view
// 					}
// 				);
// 			};
// 			event.preventDefault();
// 			// event.stopPropagation();
// 		});
// 		// event update when url change
// 		self.app._Router.AddCallback(
// 			this.form.parents('[page-name]:first').attr('page-name'),
// 			function(url){
// 				// active post viewing
// 				var s = url.match(/[a-z0-9]{24}/g);
// 				if (s != null && s.length > 0) {
// 					var post_id 	= s[0];
// 					self.form.find('.post').removeClass('active');
// 					self.form.find('.post[post-id='+post_id+']').addClass('active');
// 				};
// 				// update tab and tabmenu
// 				try{
// 					var params 	= url.split('?', 2)[1].split('&');
// 					for (var i in params) {
// 						l 	= params[i].split('=');
// 						if (l[0] == "tab") {
// 							var new_tab 	= l[1];
// 						};
// 					};
// 				}catch(e){};
// 				if (new_tab != undefined) {
// 					var new_obj 	= self.form.find('.tabmenu:first>li[md-tab='+new_tab+']');
// 					if (new_obj.length = 1 && !new_obj.hasClass('active')) {
// 						var old_obj 	= self.form.find('.tabmenu:first>li.active');
// 						var objs 		= self.form.find('.tabmenu:first>li').removeClass('active');
// 						new_obj.addClass('active');

// 						// store old list
// 						var old_tab 	= old_obj.attr('md-tab');
// 						self.form.find('.posts:first .post').remove();
// 						// self.store[old_tab] 	= self.form.find('.posts:first .post').detach();

// 						// if (typeof(self.store[new_tab]) != "undefined") {
// 						// 	self.form.find('.posts:first').append(self.store[new_tab]);
// 						// }else{
// 							self.Load( url, {});
// 						// }
// 						// add class tab to posts
// 						self.form.find('.posts:first').removeClass(old_tab).addClass(new_tab);
// 					};
// 				};
// 			}
// 		);
// 		////////////// modal for manager option ///////////
// 		this.modal 	= $('<div class="modal fade"role="dialog" aria-hidden="true" data-backdrop="static"><div class="col-xs-10 col-md-offset-1"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4 class="modal-title"></h4></div><div class="modal-body"></div><div class="modal-footer"></div></div></div></div>').modal({ "show": false}).appendTo(self.form);
// 		this.modal_title 	= this.modal.find('.modal-title:first');
// 		this.modal_body 	= this.modal.find('.modal-body:first');
// 		this.modal_footer 	= this.modal.find('.modal-footer:first');
// 		this.modal.on('hidden.bs.modal', function(event) {
// 			self.form.find('.manager .btn').removeAttr('disabled');
// 		});
// 		///////// public post
// 		this.form.on('click', '.post .manager .public', function(event){
// 			var obj 		= $(this);
// 			// self.ManagerPost(obj.parents('.post:first'), 'public');
// 			var time 		= new Date().toLocaleString();
// 			self.modal_title.html("Public post");
// 			self.modal_body.html('<div class="input-group">\
// 									<input type="datetime" value="'+time+'" class="timer form-control">\
// 									<span class="input-group-btn">\
// 										<button class="btn btn-default reset" type="button"><span class="glyphicon glyphicon-repeat"></span></button>\
// 									</span>\
// 								</div>');
// 			self.modal_footer.html('<button type="button" class="btn btn-primary btn-public">Public</button>\
// 									<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

// 			self.modal_object 	= obj.parents('.post:first');
// 			self.modal.modal('show');
// 			event.preventDefault();
// 			event.stopPropagation();
// 		});
// 		// public action
// 		this.modal.on('click', '.modal-footer .btn.btn-public', function(event) {
// 			var time 	= $(this).parents('.modal:first').find('.timer:first').val();
// 			var time 	= new Date(time).getTime();
// 			var step 	= time - (new Date()).getTime();
// 			if (!isNaN(step)) {
// 				self.modal.modal('hide');
// 				self.ManagerPost(self.modal_object, {'is':'public', 'timestep': step});
// 			};
// 		});
// 		this.modal_body.on('click', '.btn.reset', function(event) { 	// reset public timer
// 			var time 	= new Date().toLocaleString();
// 			$(this).parents('.modal:first').find('.timer:first').val(time);
// 		});
		
// 		/////////private post
// 		this.form.on('click', '.post .manager .private', function(event){
// 			var obj 		= $(this);
// 			self.ManagerPost(obj.parents('.post:first'), {'is':'private'});
// 			event.preventDefault();
// 			event.stopPropagation();
// 		});
// 		//////////trash post
// 		this.form.on('click', '.post .manager .trash', function(event){
// 			var obj 		= $(this);
// 			// self.ManagerPost(obj.parents('.post:first'), {'is':'trash'});
// 			self.modal_title.html("Trash post");
// 			self.modal_body.html('Move this post to trash ?');
// 			self.modal_footer.html('<button type="button" class="btn btn-danger btn-trash" data-dismiss="modal">Trash</button>\
// 									<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

// 			self.modal_object 	= obj.parents('.post:first');
// 			self.modal.modal('show');
// 			event.preventDefault();
// 			event.stopPropagation();
// 		});
// 		// trash action
// 		this.modal.on('click', '.modal-footer .btn.btn-trash', function(event) {
// 			self.ManagerPost(self.modal_object, {'is':'trash'});
// 		});
// 		///////////restore post
// 		this.form.on('click', '.post .manager .restore', function(event){
// 			var obj 		= $(this);
// 			self.modal_title.html("Restore post");
// 			self.modal_body.html('Restore this post to private box?');
// 			self.modal_footer.html('<button type="button" class="btn btn-success btn-restore" data-dismiss="modal">Restore</button>\
// 									<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

// 			self.modal_object 	= obj.parents('.post:first');
// 			self.modal.modal('show');
// 			event.preventDefault();
// 			event.stopPropagation();
// 		});
// 		// restore action
// 		this.modal.on('click', '.modal-footer .btn.btn-restore', function(event) {
// 			self.ManagerPost(self.modal_object, {'is':'restore'});
// 		});
// 		//////////update post
// 		this.form.on('click', '.post .manager .update', function(event){
// 			var obj 		= $(this);
// 			self.modal_title.html("Update post");
// 			self.modal_body.html('Update this post to private box?');
// 			self.modal_footer.html('<button type="button" class="btn btn-success btn-update" data-dismiss="modal">Update</button>\
// 									<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

// 			self.modal_object 	= obj.parents('.post:first');
// 			self.modal.modal('show');
// 			event.preventDefault();
// 			event.stopPropagation();
// 		});
// 		// update action
// 		this.modal.on('click', '.modal-footer .btn.btn-update', function(event) {
// 			self.ManagerPost(self.modal_object, {'is':'update'});
// 		});
// 		//////////join post
// 		this.form.on('click', '.post .manager .join', function(event){
// 			var obj 	= $(this);
// 			var post 	= obj.parents('.post:first');
// 			//
// 			var form 	= $('<div class="row"><div class="col-sm-6"><label>Current Post</label><select class="form-control join-type"><option value="append">Append to Second Post</option><option value="update">Update over Second Post</option></select><div class="current-post"></div></div><div class="col-sm-6"><label>Second Post</label><div class="input-group"><input type="text" class="form-control search"><span class="input-group-btn"><button class="btn btn-default" type="button">Search</button></span></div><div class="join-posts"></div></div></div>');
// 			var current_obj 	= post.clone().appendTo(form.find('.current-post:first'));
// 			// remove control dropdown menu
// 			current_obj.find('.manager').remove();
// 			// event search post
// 			form.find('.search').bind('change', function(event){
// 				var search 			= $(this).val().trim();
// 				if (search.length > 0) {
// 					var query			= {"action": "search"};
// 					query['module'] 	= self.form.attr('module-id');
// 					query['post'] 		= post.attr('post-id');
// 					query['search']		= search;
// 					query['count']		= 10;
// 					// load search data
// 					self.app._ProcessBar.Reset();
// 					self.app._ProcessBar.Run(50);
// 					PageAjax({
// 						type: "post",
// 						dataType: "json",
// 						url: window.location.href,
// 						data: query
// 					}).done(function(result){
// 						console.debug(result);
// 						self.app._ProcessBar.Run(100);
// 						if (result['post'] != undefined) {
// 							var p 	= $(self.Render('post', result['post']));
// 							p.find('.manager').remove();
// 							form.find('.join-posts').html(p);
// 							self.Refesh();
// 						};
// 					});
// 				};
// 				}).val(current_obj.find('.title a:first').html()+" "+current_obj.find('.subtitle:first').html()).trigger('change');

// 			self.modal_title.html("Join post");
// 			self.modal_body.html(form);
// 			self.modal_footer.html('<button type="button" class="btn btn-success btn-join" data-dismiss="modal">Join</button><button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

// 			self.modal_object 	= post;
// 			self.modal.modal('show');
// 			event.preventDefault();
// 			event.stopPropagation();
// 		});
// 		// join action
// 		this.modal.on('click', '.modal-footer .btn.btn-join', function(event) {
// 			var current_id 	= self.modal_body.find('.current-post .post[post-id]:first').attr('post-id');
// 			var join_id 	= self.modal_body.find('.join-posts .post.active[post-id]:first').attr('post-id');
// 			if (current_id != join_id) {
// 				var query 		= {'is':'join'};
// 				var join_type 	= self.modal_body.find('.join-type:first').val();
// 				console.debug(current_id, join_id,join_type);

// 				if (join_type == "update") {
// 					query['first_id'] 	= current_id;
// 					query['second_id'] 	= join_id;
// 				}else{
// 					query['first_id'] 	= join_id;
// 					query['second_id'] 	= current_id;
// 				};
// 				self.ManagerPost(self.modal_object, query);
// 			};
// 		});
// 		///////edit post
// 		this.form.on('click', '.post .manager .edit', function(event){
// 			var obj 		= $(this);
// 			//ajax
// 			var post 			= obj.parents('.post:first');
// 			var query			= {"action": "edit"};
// 			query['module'] 	= self.form.attr('module-id');
// 			query['post'] 		= post.attr('post-id');
// 			// load data
// 			self.app._ProcessBar.Reset();
// 			self.app._ProcessBar.Run(50);
// 			PageAjax({
// 				type: "post",
// 				dataType: "json",
// 				url: window.location.href,
// 				data: query
// 			}).done(function(result) {
// 				self.app._ProcessBar.Run(100);
// 				if (result['post'] != undefined) {
// 					var form 	= $('<ul class="nav nav-tabs" role="tablist"><li class="active"><a href="#movie" role="tab" data-toggle="tab">Movie</a></li><li><a href="#info" role="tab" data-toggle="tab">Profile</a></li></ul><div class="tab-content edit-post"><div class="tab-pane row active movie" id="movie"><div class="col-sm-12"><div class="row menu"><div class="col-sm-6"><label>Chap</label><div class="btn-toolbar" role="toolbar"><div class="btn-group"><button type="button" title="Edit Chap" class="btn btn-group-sm btn-primary btn-chap-edit"><span class="glyphicon glyphicon-edit"></span></button><button type="button" title="Append Chap" class="btn btn-group-sm btn-success btn-chap-append"><span class="glyphicon glyphicon-plus"></span></button></div><div class="btn-group"><button type="button" title="Move Chap Up" class="btn btn-group-sm btn-info btn-chap-up"><span class="glyphicon glyphicon-circle-arrow-up"></span></button><button type="button" title="Move Chap Down" class="btn btn-group-sm btn-warning btn-chap-down"><span class="glyphicon glyphicon-circle-arrow-down"></span></button></div><div class="btn-group"><button type="button" title="Remove Chap" class="btn btn-group-sm btn-danger btn-chap-remove"><span class="glyphicon glyphicon-trash"></span></button></div></div></div><div class="col-sm-6"><label>Server</label><div class="btn-toolbar" role="toolbar"><div class="btn-group"><button type="button" class="btn btn-group-sm btn-primary btn-srv-edit"><span class="glyphicon glyphicon-edit"></span></button><button type="button" class="btn btn-group-sm btn-success btn-srv-append"><span class="glyphicon glyphicon-plus"></span></button></div><div class="btn-group"><button type="button" class="btn btn-group-sm btn-info btn-srv-left"><span class="glyphicon glyphicon-circle-arrow-left"></span></button><button type="button" class="btn btn-group-sm btn-warning btn-srv-right"><span class="glyphicon glyphicon-circle-arrow-right"></span></button></div><div class="btn-group"><button type="button" class="btn btn-group-sm btn-danger btn-srv-remove"><span class="glyphicon glyphicon-trash"></span></button></div></div></div></div><div class="row inset select chaps"></div></div><div class="col-sm-12"><div class="panel panel-default"><div class="panel-heading">Editor</div><div class="panel-body chap-config"></div></div></div></div><div class="tab-pane row info" id="info"><div class="col-sm-6"><label>Title</label><input type="text" name="title" class="form-control"></div><div class="col-sm-6"><label>Sub Title</label><input type="text" name="subtitle" class="form-control"></div><div class="col-sm-6"><label>Status</label><input type="text" name="status" class="form-control"></div><div class="col-sm-6"><label>Thời lượng</label><input type="text" name="length" class="form-control"></div><div class="col-sm-6"><label>Đạo diễn</label><input type="text" name="director" class="form-control"></div><div class="col-sm-6"><label>Quốc gia</label><input type="text" name="country" class="form-control"></div><div class="col-sm-6"><label>Năm phát hành</label><input type="text" name="year" class="form-control"></div><div class="col-sm-6"><label>Thể loại</label><textarea class="form-control" name="category" rows="3"></textarea></div><div class="col-sm-6"><label>Diễn viên</label><textarea class="form-control" name="stars" rows="3"></textarea></div><div class="col-sm-6"><label>Nguồn</label><textarea class="form-control" name="source" rows="3"></textarea></div><div class="col-sm-6"><label>Giới thiệu</label><textarea class="form-control" name="descript_long" rows="10"></textarea></div><div class="col-sm-6"><label>Giới thiệu Ngắn</label><textarea class="form-control" name="descript_short" rows="10"></textarea></div></div></div>');
					
// 					///// insert info /////
// 					var menu 	= form.find('.menu:first');
// 					menu.affix({
// 						offset: {
// 							top: 200
// 						}
// 					});
// 					// all chaps information
// 					$.each(result['post']['chaps'], function(i, chap){
// 						var mv_found 	= false;
// 						for (var i = 0; i < result['post']['movie'].length; i++) {
// 							var mv 	= result['post']['movie'][i];
// 							if (mv['id'].length > 0 && mv['id'] == chap['id']) {
// 								mv['server'] = chap['server'];
// 								mv_found 	= true;
// 								break;
// 							};
// 						};
// 						if (!mv_found) {
// 							chap['id'] 	= '';
// 							chap['name'] = 'unknown';
// 							result['post']['movie'].push(chap);
// 						};
// 					});
// 					// list chap in movie
// 					var f_chaps 	= form.find('.chaps');
// 					$.each(result['post']['movie'], function(i, chap){
// 						self._Chap_Json2Obj(chap).appendTo(f_chaps);
// 					});
// 					// movie information
// 					console.debug(result['post']);
// 					for (var k in result['post']) {
// 						if (k != "movie" && k != "chaps"){
// 							var obj 	= form.find('.tab-pane [name='+k+']');
// 							if (obj.length > 0) {
// 								data 	= result['post'][k];
// 								if ($.type(data) == "array") {
// 									data 	= data.join('\n');
// 								}else if($.type(data) == "object") {
// 									data 	= JSON.stringify(data);
// 								};
// 								obj.val(data);
// 							};
// 						};
// 					};
// 					// insert modal
// 					self.modal_title.html("Edit Movie");
// 					self.modal_body.html(form);
// 					self.modal_footer.html('<button type="button" class="btn btn-warning btn-edit" data-dismiss="modal">Save</button><button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

// 					self.modal_object 	= post;
// 					self.modal.modal('show');
// 				};
// 			}).error(function(e){
// 				console.error(e);
// 			});
// 			event.preventDefault();
// 			event.stopPropagation();
// 		});
// 		// edit action
// 		this.modal.on('click', '.modal-footer .btn.btn-edit', function(event) {
// 			var query 		= {'is':'edit'};
// 			var args 		= self.modal_body.find('.tab-pane.info [name]');
// 			$.each(args, function(i, v){
// 				var obj 	= $(v);
// 				var name 	= obj.attr('name');
// 				var data 	= obj.val();
// 				query['p_'+name] 	= data;
// 			});
// 			var chaps 			= self.modal_body.find('.tab-pane.movie .chaps .chap');
// 			query['p_movie'] 	= JSON.stringify(self._Chaps_Obj2Json(chaps));
// 			self.ManagerPost(self.modal_object, query);
// 		});
// 		// event chap edit
// 		self.modal.on('click', '.edit-post .menu .btn-chap-edit', function(event){
// 			var chaps 		= self.modal.find('.edit-post .chaps');
// 			var selected 	= chaps.children('.chap.active');
// 			if (selected.length > 0) {
// 				chaps.scrollTop(selected.position().top + chaps.scrollTop() - 150);
// 				var config 		= self.modal.find('.edit-post .chap-config:first').html('<div class="row chap-editor"><div class="col-xs-12"><label>Chap Name</label><input type="text" class="form-control chap-name" placeholder="chap name"></div><div class="col-xs-12"><label>Chap JSON</label><textarea class="form-control chap-json" placeholder="chap name"></textarea></div><div class="col-xs-6 col-xs-offset-3"><div class="btn btn-primary chap-update">Update</div><div class="btn btn-success chap-close">Close</div></div></div>');

// 				var chap_json 	= self._Chap_Obj2Json(selected);
// 				// change name -> change config
// 				var chap_name_obj 		= config.find('.chap-name:first');
// 				var chap_json_obj 		= config.find('.chap-json:first');
// 				var _Chap_Update_Data 	= function(){
// 					chap_name_obj.val(chap_json['name']);
// 					chap_json_obj.val(js_beautify(JSON.stringify(chap_json),{
// 						'indent_size': 1,
// 						'indent_char': '\t'
// 					}));
// 				};
// 				_Chap_Update_Data();
// 				// event
// 				chap_name_obj.bind('change', function(event){
// 					chap_json['name'] 	= $(this).val();
// 					_Chap_Update_Data();
// 				});
// 				chap_json_obj.bind('change', function(event){
// 					chap_json 	= JSON.parse($(this).val());
// 					_Chap_Update_Data();
// 				});
// 				// update chap
// 				config.find('.btn.chap-update').bind('click', function(event){
// 					console.debug(chap_json);
// 					var new_obj = self._Chap_Json2Obj(chap_json).insertAfter(selected).addClass('active');
// 					selected.remove();
// 					selected = new_obj;
// 				});
// 			}else{
// 				alert('plz select one chap!');
// 			};
// 		});
// 		// event chap append
// 		self.modal.on('click', '.edit-post .menu .btn-chap-append', function(event){
// 			var chaps 		= self.modal.find('.edit-post .chaps');
// 			var selected 	= chaps.children('.chap.active');
// 			var new_obj 	= self._Chap_Json2Obj({});
// 			if (selected.length > 0) {
// 				selected.after(new_obj);
// 			}else{
// 				chaps.append(new_obj);
// 			};
// 			new_obj.click();
// 			self.modal.find('.edit-post .menu .btn-chap-edit').click();
// 		});
// 		// event chap up
// 		self.modal.on('click', '.edit-post .menu .btn-chap-up', function(event){
// 			var selected 	= self.modal.find('.edit-post .chaps .chap.active');
// 			if (selected.length > 0) {
// 				var before 	= selected.prev();
// 				if (before.length > 0) {
// 					before.before(selected.detach());
// 				};
// 			};
// 		});
// 		// event chap up
// 		self.modal.on('click', '.edit-post .menu .btn-chap-down', function(event){
// 			var selected 	= self.modal.find('.edit-post .chaps .chap.active');
// 			if (selected.length > 0) {
// 				var after 	= selected.next();
// 				if (after.length > 0) {
// 					after.after(selected.detach());
// 				};
// 			};
// 		});
// 		self.modal.on('click', '.edit-post .menu .btn-chap-remove', function(event){
// 			var selected 	= self.modal.find('.edit-post .chaps .chap.active');
// 			if (selected.length > 0) {
// 				if (confirm('Are you sure you want to remove selected chap?')) {
// 					selected.remove();
// 				};
// 			};
// 		});
// 		//////
// 		var _Modal_Edit_Chap_Select  = function(){
// 			// clear update chap/server form
// 			self.modal.find('.edit-post .chap-config:first').children().hide();
// 		};
// 		// event click chap
// 		self.modal.on('click', '.edit-post .chap', function(event){
// 			var obj 	= $(this);
// 			if (!obj.hasClass('active')) {
// 				obj.parent().find('.chap.active, .chap .srv.active').removeClass('active');
// 				obj.addClass('active');
// 				_Modal_Edit_Chap_Select();
// 			};
// 			event.preventDefault();
// 			event.stopPropagation();
// 		});
// 		// show server name/server/parts config
// 		self.modal.on('click', '.edit-post .chap .srvs .srv', function(event){
// 			var obj 	= $(this);
// 			if (!obj.hasClass('active')) {
// 				self.modal.find('.edit-post .chap.active, .edit-post .chap .srv.active').removeClass('active');
// 				obj.addClass('active');
// 				obj.parents('.chap:first').addClass('active');
// 				_Modal_Edit_Chap_Select();
// 			};
// 			event.preventDefault();
// 			event.stopPropagation();
// 		});
// 		//////////////// edit server modal event
// 		self.modal.on('click', '.edit-post .menu .btn-srv-edit', function(event){
// 			var chaps 			= self.modal.find('.edit-post .chaps');
// 			var chap_selected 	= chaps.children('.chap.active');
// 			var srv_selected 	= chap_selected.find('.srv.active');
// 			if (srv_selected.length > 0) {
// 				chaps.scrollTop(chap_selected.position().top + chaps.scrollTop() - 150);
// 				var config 		= self.modal.find('.edit-post .chap-config:first').html('<div class="row srv-editor"><div class="col-xs-12"><label>JSON</label><textarea class="form-control srv-json" placeholder="server json"></textarea></div><div class="col-xs-12"><label>Name</label><input type="text" class="form-control srv-name" placeholder="server name"></div><div class="col-xs-12"><label>Parts</label><div class="row part-edit"><ul class="col-xs-4 inset parts"><li class="part">1-a</li><li class="part">1-b</li></ul><div class="col-xs-8 part-editor"><label>Name</label><input type="text" class="form-control part-name" placeholder="part name"><label>Link</label><input type="text" class="form-control part-link" placeholder="part link"><label>Source</label><textarea class="form-control part-source" placeholder="part source"></textarea><label>JSON</label><textarea class="form-control part-json" placeholder="part json"></textarea></div></div></div><div class="col-xs-6 col-xs-offset-3"><div class="btn btn-primary srv-update">Update</div><div class="btn btn-success srv-close">Close</div></div></div>');

// 				var srv_json 	= self._Server_Obj2Json(srv_selected);
// 				// console.debug(js_beautify(srv_json));
// 				// change name -> change config
// 				var srv_name_obj 		= config.find('.srv-name:first');
// 				var srv_json_obj 		= config.find('.srv-json:first');
// 				var srv_parts_obj 		= config.find('.part-edit .parts:first');
// 				var _Srv_Update_Data 	= function(){
// 					srv_name_obj.val(srv_json['name']);
// 					srv_json_obj.val(js_beautify(JSON.stringify(srv_json),{
// 						'indent_size': 1,
// 						'indent_char': '\t'
// 					}));
// 					srv_parts_obj.html('');
// 					for (var i = 0; i < srv_json['part'].length; i++) {
// 						var part 		= srv_json['part'][i];
// 						var part_obj 	= $('<li class="part" data="'+Base64.encode(JSON.stringify(part))+'">'+part['name']+'</li>');
// 						srv_parts_obj.append(part_obj)
// 					};
// 				};
// 				_Srv_Update_Data();
// 				// event
// 				srv_name_obj.bind('change', function(event){
// 					srv_json['name'] 	= $(this).val();
// 					_Srv_Update_Data();
// 				});
// 				srv_json_obj.bind('change', function(event){
// 					srv_json 	= JSON.parse($(this).val());
// 					_Srv_Update_Data();
// 				});
// 				srv_parts_obj.on('click','.part', function(event){
// 					var part_json 	= JSON.parse(Base64.decode($(this).attr('data')));
// 					config.find('.part-edit .part-editor .part-json').val(js_beautify(part_json));
// 					_Srv_Update_Data();
// 				});
// 				// update chap
// 				config.find('.btn.srv-update').bind('click', function(event){
// 					console.debug(srv_json);
// 					var new_obj = self._Server_Json2Obj(srv_json).insertAfter(srv_selected).addClass('active');
// 					srv_selected.remove();
// 					srv_selected = new_obj;
// 				});
// 			}else{
// 				alert('plz select one server!');
// 			};
// 		});
// 		// event server append
// 		self.modal.on('click', '.edit-post .menu .btn-srv-append', function(event){
// 			var chap 		= self.modal.find('.edit-post .chaps .chap.active .srvs>ul');
// 			var selected 	= chap.find('.srv.active');
// 			var new_obj 	= self._Server_Json2Obj({});
// 			if (selected.length > 0) {
// 				selected.after(new_obj);
// 			}else{
// 				chap.append(new_obj);
// 			};
// 			new_obj.click();
// 			self.modal.find('.edit-post .menu .btn-srv-edit').click();
// 		});
// 		// event server up
// 		self.modal.on('click', '.edit-post .menu .btn-srv-left', function(event){
// 			var selected 	= self.modal.find('.edit-post .chap.active .srv.active');
// 			if (selected.length > 0) {
// 				var before 	= selected.prev();
// 				if (before.length > 0) {
// 					before.before(selected.detach());
// 				};
// 			};
// 		});
// 		// event server up
// 		self.modal.on('click', '.edit-post .menu .btn-srv-right', function(event){
// 			var selected 	= self.modal.find('.edit-post .chap.active .srv.active');
// 			if (selected.length > 0) {
// 				var after 	= selected.next();
// 				if (after.length > 0) {
// 					after.after(selected.detach());
// 				};
// 			};
// 		});
// 		// remove server
// 		self.modal.on('click', '.edit-post .menu .btn-srv-remove', function(event){
// 			var selected 	= self.modal.find('.edit-post .chap.active .srv.active');
// 			if (selected.length > 0) {
// 				if (confirm('Are you sure you want to remove selected server ?')) {
// 					selected.remove();
// 				};
// 			};
// 		});
// 		////////////delete post
// 		this.form.on('click', '.post .manager .delete', function(event){
// 			var obj 		= $(this);
// 			// self.ManagerPost(obj.parents('.post:first'), {'is':'restore'});
// 			self.modal_title.html("Restore post");
// 			self.modal_body.html('Delete this box?');
// 			self.modal_footer.html('<button type="button" class="btn btn-danger btn-delete" data-dismiss="modal">Delete</button><button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

// 			self.modal_object 	= obj.parents('.post:first');
// 			self.modal.modal('show');
// 			event.preventDefault();
// 			event.stopPropagation();
// 		});
// 		// delete action
// 		this.modal.on('click', '.modal-footer .btn.btn-delete', function(event) {
// 			self.ManagerPost(self.modal_object, {'is':'delete'});
// 		});
		
// 	},
// 	_Chaps_Obj2Json: function(chaps){
// 		var self 	= this;
// 		var result 	= [];
// 		$.each(chaps, function(i, v){
// 			var chap = $(v);
// 			result.push(self._Chap_Obj2Json(chap));
// 		});
// 		return result;
// 	},
// 	_Chap_Json2Obj: function(chap){
// 		var self 		= this;
// 		if (chap['name'] == undefined) {
// 			chap['name'] 	= 'unknown';
// 		};
// 		if (chap['id'] == undefined) {
// 			chap['id'] 		= '';
// 		};
// 		if (chap['server'] == undefined) {
// 			chap['server'] 	= [];
// 		};
// 		//
// 		f_chap 			= $('<div class="option chap row" chap-id="'+chap['id']+'" chap-name="'+chap['name']+'">'+
// 								'<div class="col-xs-2 name">'+chap['name']+'</div>'+
// 								'<div class="col-xs-10 srvs"><ul></ul></div>'+
// 							'</div>');
// 		var f_srvs 		= f_chap.find('.srvs>ul');
// 		$.each(chap['server'], function(i, srv){
// 			f_srvs.append(self._Server_Json2Obj(srv));
// 		});
// 		// f_chap.attr('data', Base64.encode(JSON.stringify(chap)));
// 		return f_chap;
// 	},
// 	_Chap_Obj2Json: function(chap){
// 		var self 		= this;
// 		var chap_json 	= {
// 			"id"		: chap.attr('chap-id'),
// 			"name"		: chap.attr('chap-name'),
// 			"server"	: []
// 		};
// 		var srvs 		= chap.find('.srv');
// 		$.each(srvs, function(i, v){
// 			var srv 	= $(v);
// 			chap_json['server'].push(self._Server_Obj2Json(srv));
// 		});
// 		return chap_json;
// 	},
// 	_Server_Json2Obj: function(srv){
// 		if (srv['name'] == undefined) {
// 			srv['name'] = 'unknown';
// 		};
// 		if (srv['part'] == undefined) {
// 			srv['part'] = [];
// 		};
// 		var f_srv 	= ""
// 		$.each(srv['part'], function(i, part){
// 			f_srv 	+= '<li class="part">'+part['name']+'</li>';
// 		});
// 		f_srv 	= '<li class="col-sm-4 srv" data="'+Base64.encode(JSON.stringify(srv))+'">'+
// 					'<div class="row"><div class="col-xs-4">Name : </div><div class="col-xs-8 srv-name">'+srv['name']+'</div></div>'+
// 					'<div class="row srv-parts"><ul>'+f_srv+'</ul></div>'+
// 				'</li>';
// 		return $(f_srv);
// 	},
// 	_Server_Obj2Json: function(srv){
// 		return JSON.parse(Base64.decode(srv.attr('data')));
// 	},
// 	Load: function(url, query){
// 		var self 	= this;
// 		if (typeof(query['post']) != "undefined") {
// 			if (typeof(query['time']) == "string") {
// 				$.each(self.form.find('.main .post'), function(index, value){
// 					var o 	= $(value);
// 					var t 	= o.find('.time:first').attr('time');
// 					if (t == query['time']) {
// 						query['post'].push(o.attr('post-id'));
// 					};
// 				});
// 			};
// 			if (typeof(query['view']) == "string") {
// 				$.each(self.form.find('.main .post'), function(index, value){
// 					var o 	= $(value);
// 					var v 	= o.find('.view .value:first').html();
// 					if (v == query['view']) {
// 						query['post'].push(o.attr('post-id'));
// 					};
// 				});
// 			};
// 			// remove duplicate post
// 			var posts 		= []
// 			$.each(query['post'], function(i, v){
// 				if($.inArray(v, posts) === -1) posts.push(v);
// 			});
// 			query['post'] 	= posts.join(',');
// 		};
// 		///
// 		query['module'] 	= self.form.attr('module-id');
// 		self.app._ProcessBar.Reset();
// 		self.app._ProcessBar.Run(50);
// 		PageAjax({
// 			type: "post",
// 			dataType: "json",
// 			url: url,
// 			data: query
// 		}).done(function(result) {
// 			if (result['post'] != undefined) {
// 				self.app._ProcessBar.Run(100);
// 				self.posts.append(self.Render('post', result['post']));
// 				self.Refesh();
// 			}
// 		}).error(function(e){
// 			console.error(e);
// 		});
// 	},
// 	ManagerPost: function(post, query){
// 		var self 	= this;
// 		query['action']		= "manager";
// 		query['module'] 	= self.form.attr('module-id');
// 		query['post'] 		= post.attr('post-id');

// 		console.debug(query);

// 		self.app._ProcessBar.Reset();
// 		self.app._ProcessBar.Run(50);
// 		PageAjax({
// 			type: "post",
// 			dataType: "json",
// 			url: window.location.href,
// 			data: query
// 		}).done(function(result) {
// 			self.app._ProcessBar.Run(100);
// 			if (result['error'] == 0) {
// 				var mng 	= post.find('.manager');
// 				// if (query['is'] == "trash" || query['is'] == "restore") {
// 				if (query['is'] == "trash" || query['is'] == "restore" || query['is'] == "delete") {
// 					post.remove();
// 				}else if (query['is'] == "public" || query['is'] == "private") {
// 					mng.children().removeAttr('disabled');
// 					post.removeClass('public private').addClass(query['is']);
// 				};
// 			};
// 		}).error(function(e){
// 			console.error(e);
// 		});
// 	},
// 	Render: function(tpl, args){
// 		console.debug(args);
// 		var self 		= this;
// 		var templates 	= "";
// 		$.each(args, function(index, value){
// 			var template = self.template[tpl];
// 			$.each(value, function(k, v) {
// 				template = template.split('{{ '+k+' }}').join(v);
// 			});
// 			templates 	+= template;
// 		});
// 		return templates;
// 	},
// 	Refesh: function(){
// 		var self 			= this;
// 		// setting update
// 		// update class
// 		if (typeof(self.setting['class']) != "undefined") {
// 			$.each(self.setting['class'], function(key, value){
// 				var obj 	= self.form.find('.'+key);
// 				$.each(obj, function(i, v){
// 					var o = $(v);
// 					if (!o.data('md-classed')) {
// 						o.addClass(value)
// 						 .data('md-classed', true);
// 					};
// 				});
// 			});
// 		};
// 		// view user info
// 		if (typeof(self.setting['user']) != "undefined") {
// 			var obj = self.form.find('.post .user .by');
// 			if (self.setting['user']) {
// 				obj.show();
// 			}else{
// 				obj.hide();
// 			};
// 		};
// 		// update blank
// 		if (typeof(self.setting['blank']) != "undefined" && self.setting['blank']) {
// 			var posts 	= self.form.find('.posts .post');
// 			$.each(posts, function(key, value){
// 				var obj = $(value);
// 				if (!obj.data('md-blanked')) {
// 					obj.find('.image a').attr('target', '_blank');
// 					obj.find('.title a').attr('target', '_blank');
// 					obj.data('md-blanked', true);
// 				};
// 			});
// 		}else{
// 			self.form.find('.post .image a:not([site-goto]), .post .title a:not([site-goto])').attr('site-goto', '+');
// 		}
// 		/////
// 		var update_fb_info 	= false;
// 		// view button
// 		if (typeof(self.setting['view']) != "undefined" && self.setting['view']) {
// 			self.form.find('.post .user .info .view').show();
// 		};
// 		// like button
// 		if (typeof(self.setting['like']) != "undefined" && self.setting['like']) {
// 			self.form.find('.post .user .info .like').show();
// 			update_fb_info 		= true;
// 		};
// 		// share button
// 		if (typeof(self.setting['share']) != "undefined" && self.setting['share']) {
// 			self.form.find('.post .user .info .share').show();
// 			update_fb_info 		= true;
// 		};
// 		// comment button
// 		if (typeof(self.setting['comment']) != "undefined" && self.setting['comment']) {
// 			self.form.find('.post .user .info .comment').show();
// 			update_fb_info 		= true;
// 		};
// 		if (update_fb_info) {
// 			var posts 	= self.form.find('.posts .post');
// 			$.each(posts, function(key, value){
// 				var obj = $(value);
// 				if (!obj.data('md-fb-info-updated')) {
// 					var link 	= obj.find('.title a:first')[0].href;
// 					$.getJSON("http://graph.facebook.com/?id=" + link, function(data){
// 					// $.getJSON("http://graph.facebook.com/?id=https://www.facebook.com/", function(data){
// 						obj.find('.info .like:first').append(typeof(data['likes']) != "undefined" ? data['likes']: 0);
// 						obj.find('.info .comment:first').append(typeof(data['comments']) != "undefined" ? data['comments']: 0);
// 						obj.find('.info .share:first').append(typeof(data['shares']) != "undefined" ? data['shares']: 0);
// 					});
// 					obj.data('md-fb-info-updated', true);
// 				};
// 			});
// 		};
// 		// view more button
// 		if (typeof(self.setting['more']) != "undefined") {
// 			var more = self.form.find('.footer .view-more');
// 			if (!more.data('md-mored')) {
// 				if (self.setting['more']) {
// 					more.show();
// 				}else{
// 					more.hide();
// 				};
// 				more.data('md-mored', true);
// 			};
// 		};
// 		// update height
// 		if (typeof(self.setting['max-height']) == "number") {
// 			if (self.setting['max-height'] > 0) {
// 				var obj = self.form.find('.main:first');
// 				if (!obj.data('md-heighted')) {
// 					obj.css("max-height", self.setting['max-height']+ "vh");
// 					obj.data('md-heighted', true);
// 				};
// 			};
// 		};
// 	}
// };



PageModuleCineManager.prototype = new Module();
PageModuleCineManager.prototype.constructor = PageModuleCineManager;
function PageModuleCineManager(app){
	Module.call(this, app);
	$.extend(this.setting, {
		"header": 	true,
		"onrouter": true
	});
};
PageModuleCineManager.prototype.Init = function(form) {
	Module.prototype.Init.call(this, form);
	var self 	= this;
	
	//  view more
	this.form.on('click', '.view-more', function(event){
		var obj 	= self.form.find('.posts .post');
		if (obj.length > 0) {
			// var time 	= obj.find('.time:first').attr('time');
			// var post 	= [obj.attr('post-id')];
			// var view 	= obj.find('.view .value:first').html();
			self.Load({
				"query":{
					"skip": obj.length
				}
			});
		};
		event.preventDefault();
		// event.stopPropagation();
	});
	// event update when url change
	self.onRouter(
		function(result){
			// active post viewing
			if (result['post'] != undefined) {
				self.form.find('.post').removeClass('active');
				self.form.find('.post[post-id='+result['post']+']').addClass('active');
			};
			// update tab and tabmenu
			if (result['param']['tab'] != undefined) {
				var new_obj 	= self.form.find('.tabmenu:first>li[md-tab='+result['param']['tab']+']');
				if (new_obj.length = 1 && !new_obj.hasClass('active')) {
					var old_obj 	= self.form.find('.tabmenu:first>li.active');
					var objs 		= self.form.find('.tabmenu:first>li').removeClass('active');
					new_obj.addClass('active');
					// store old list
					var old_tab 	= old_obj.attr('md-tab');
					self.form.find('.posts:first .post').remove();
					
					self.Load();
					// add class tab to posts
					self.form.find('.posts:first').removeClass(old_tab).addClass(result['param']['tab']);
				};
			};
		},{"post": 1, "param": 1}
	);
	////////////// modal for manager option ///////////
	this.modal 	= $('<div class="modal fade"role="dialog" aria-hidden="true" data-backdrop="static"><div class="col-xs-10 col-md-offset-1"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4 class="modal-title"></h4></div><div class="modal-body"></div><div class="modal-footer"></div></div></div></div>').modal({ "show": false}).appendTo(self.form);
	this.modal_title 	= this.modal.find('.modal-title:first');
	this.modal_body 	= this.modal.find('.modal-body:first');
	this.modal_footer 	= this.modal.find('.modal-footer:first');
	this.modal.on('hidden.bs.modal', function(event) {
		self.form.find('.manager .btn').removeAttr('disabled');
	});
	///////// public post
	this.form.on('click', '.post .manager .public', function(event){
		var obj 		= $(this);
		// self.ManagerPost(obj.parents('.post:first'), 'public');
		var time 		= new Date().toLocaleString();
		self.modal_title.html("Public post");
		self.modal_body.html('<div class="input-group">\
								<input type="datetime" value="'+time+'" class="timer form-control">\
								<span class="input-group-btn">\
									<button class="btn btn-default reset" type="button"><span class="glyphicon glyphicon-repeat"></span></button>\
								</span>\
							</div>');
		self.modal_footer.html('<button type="button" class="btn btn-primary btn-public">Public</button>\
								<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

		self.modal_object 	= obj.parents('.post:first');
		self.modal.modal('show');
		event.preventDefault();
		event.stopPropagation();
	});
	// public action
	this.modal.on('click', '.modal-footer .btn.btn-public', function(event) {
		var time 	= $(this).parents('.modal:first').find('.timer:first').val();
		var time 	= new Date(time).getTime();
		var step 	= time - (new Date()).getTime();
		if (!isNaN(step)) {
			self.modal.modal('hide');
			self.ManagerPost(self.modal_object, {'is':'public', 'timestep': step});
		};
	});
	this.modal_body.on('click', '.btn.reset', function(event) { 	// reset public timer
		var time 	= new Date().toLocaleString();
		$(this).parents('.modal:first').find('.timer:first').val(time);
	});
	
	/////////private post
	this.form.on('click', '.post .manager .private', function(event){
		var obj 		= $(this);
		self.ManagerPost(obj.parents('.post:first'), {'is':'private'});
		event.preventDefault();
		event.stopPropagation();
	});
	//////////trash post
	this.form.on('click', '.post .manager .trash', function(event){
		var obj 		= $(this);
		// self.ManagerPost(obj.parents('.post:first'), {'is':'trash'});
		self.modal_title.html("Trash post");
		self.modal_body.html('Move this post to trash ?');
		self.modal_footer.html('<button type="button" class="btn btn-danger btn-trash" data-dismiss="modal">Trash</button>\
								<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

		self.modal_object 	= obj.parents('.post:first');
		self.modal.modal('show');
		event.preventDefault();
		event.stopPropagation();
	});
	// trash action
	this.modal.on('click', '.modal-footer .btn.btn-trash', function(event) {
		self.ManagerPost(self.modal_object, {'is':'trash'});
	});
	///////////restore post
	this.form.on('click', '.post .manager .restore', function(event){
		var obj 		= $(this);
		self.modal_title.html("Restore post");
		self.modal_body.html('Restore this post to private box?');
		self.modal_footer.html('<button type="button" class="btn btn-success btn-restore" data-dismiss="modal">Restore</button>\
								<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

		self.modal_object 	= obj.parents('.post:first');
		self.modal.modal('show');
		event.preventDefault();
		event.stopPropagation();
	});
	// restore action
	this.modal.on('click', '.modal-footer .btn.btn-restore', function(event) {
		self.ManagerPost(self.modal_object, {'is':'restore'});
	});
	//////////update post
	this.form.on('click', '.post .manager .update', function(event){
		var obj 		= $(this);
		self.modal_title.html("Update post");
		self.modal_body.html('Update this post to private box?');
		self.modal_footer.html('<button type="button" class="btn btn-success btn-update" data-dismiss="modal">Update</button>\
								<button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

		self.modal_object 	= obj.parents('.post:first');
		self.modal.modal('show');
		event.preventDefault();
		event.stopPropagation();
	});
	// update action
	this.modal.on('click', '.modal-footer .btn.btn-update', function(event) {
		self.ManagerPost(self.modal_object, {'is':'update'});
	});
	//////////join post
	this.form.on('click', '.post .manager .join', function(event){
		var obj 	= $(this);
		var post 	= obj.parents('.post:first');
		//
		var form 	= $('<div class="row"><div class="col-sm-6"><label>Current Post</label><select class="form-control join-type"><option value="append">Append to Second Post</option><option value="update">Update over Second Post</option></select><div class="current-post"></div></div><div class="col-sm-6"><label>Second Post</label><div class="input-group"><input type="text" class="form-control search"><span class="input-group-btn"><button class="btn btn-default" type="button">Search</button></span></div><div class="join-posts"></div></div></div>');
		var current_obj 	= post.clone().appendTo(form.find('.current-post:first'));
		// remove control dropdown menu
		current_obj.find('.manager').remove();
		// event search post
		form.find('.search').bind('change', function(event){
			var search 			= $(this).val().trim();
			if (search.length > 0) {
				var query			= {"action": "search"};
				query['module'] 	= self.form.attr('module-id');
				query['post'] 		= post.attr('post-id');
				query['search']		= search;
				query['count']		= 10;
				// load search data

				self.Load({
					"query": query,
					"callback": function(result){
						console.debug(result);
						if (result['post'] != undefined) {
							var p 	= $(self.Render('post', result['post']));
							p.find('.manager').remove();
							form.find('.join-posts').html(p);
							self.Refesh();
						};
					}
				});
				// self.app._ProcessBar.Reset();
				// self.app._ProcessBar.Run(50);
				// PageAjax({
				// 	type: "post",
				// 	dataType: "json",
				// 	url: window.location.href,
				// 	data: query
				// }).done(function(result){
				// 	console.debug(result);
				// 	self.app._ProcessBar.Run(100);
				// 	if (result['post'] != undefined) {
				// 		var p 	= $(self.Render('post', result['post']));
				// 		p.find('.manager').remove();
				// 		form.find('.join-posts').html(p);
				// 		self.Refesh();
				// 	};
				// });
			};
			}).val(current_obj.find('.title a:first').html()+" "+current_obj.find('.subtitle:first').html()).trigger('change');

		self.modal_title.html("Join post");
		self.modal_body.html(form);
		self.modal_footer.html('<button type="button" class="btn btn-success btn-join" data-dismiss="modal">Join</button><button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

		self.modal_object 	= post;
		self.modal.modal('show');
		event.preventDefault();
		event.stopPropagation();
	});
	// join action
	this.modal.on('click', '.modal-footer .btn.btn-join', function(event) {
		var current_id 	= self.modal_body.find('.current-post .post[post-id]:first').attr('post-id');
		var join_id 	= self.modal_body.find('.join-posts .post.active[post-id]:first').attr('post-id');
		if (current_id != join_id) {
			var query 		= {'is':'join'};
			var join_type 	= self.modal_body.find('.join-type:first').val();
			console.debug(current_id, join_id,join_type);

			if (join_type == "update") {
				query['first_id'] 	= current_id;
				query['second_id'] 	= join_id;
			}else{
				query['first_id'] 	= join_id;
				query['second_id'] 	= current_id;
			};
			self.ManagerPost(self.modal_object, query);
		};
	});
	///////edit post
	this.form.on('click', '.post .manager .edit', function(event){
		var obj 		= $(this);
		//ajax
		var post 			= obj.parents('.post:first');
		var query			= {"action": "edit"};
		query['module'] 	= self.form.attr('module-id');
		query['post'] 		= post.attr('post-id');


		// load data

		self.Load({
			"query": query,
			"callback": function(result) {
				if (result['post'] != undefined) {
					var form 	= $('<ul class="nav nav-tabs" role="tablist"><li class="active"><a href="#movie" role="tab" data-toggle="tab">Movie</a></li><li><a href="#info" role="tab" data-toggle="tab">Profile</a></li></ul><div class="tab-content edit-post"><div class="tab-pane row active movie" id="movie"><div class="col-sm-12"><div class="row menu"><div class="col-sm-6"><label>Chap</label><div class="btn-toolbar" role="toolbar"><div class="btn-group"><button type="button" title="Edit Chap" class="btn btn-group-sm btn-primary btn-chap-edit"><span class="glyphicon glyphicon-edit"></span></button><button type="button" title="Append Chap" class="btn btn-group-sm btn-success btn-chap-append"><span class="glyphicon glyphicon-plus"></span></button></div><div class="btn-group"><button type="button" title="Move Chap Up" class="btn btn-group-sm btn-info btn-chap-up"><span class="glyphicon glyphicon-circle-arrow-up"></span></button><button type="button" title="Move Chap Down" class="btn btn-group-sm btn-warning btn-chap-down"><span class="glyphicon glyphicon-circle-arrow-down"></span></button></div><div class="btn-group"><button type="button" title="Remove Chap" class="btn btn-group-sm btn-danger btn-chap-remove"><span class="glyphicon glyphicon-trash"></span></button></div></div></div><div class="col-sm-6"><label>Server</label><div class="btn-toolbar" role="toolbar"><div class="btn-group"><button type="button" class="btn btn-group-sm btn-primary btn-srv-edit"><span class="glyphicon glyphicon-edit"></span></button><button type="button" class="btn btn-group-sm btn-success btn-srv-append"><span class="glyphicon glyphicon-plus"></span></button></div><div class="btn-group"><button type="button" class="btn btn-group-sm btn-info btn-srv-left"><span class="glyphicon glyphicon-circle-arrow-left"></span></button><button type="button" class="btn btn-group-sm btn-warning btn-srv-right"><span class="glyphicon glyphicon-circle-arrow-right"></span></button></div><div class="btn-group"><button type="button" class="btn btn-group-sm btn-danger btn-srv-remove"><span class="glyphicon glyphicon-trash"></span></button></div></div></div></div><div class="row inset select chaps"></div></div><div class="col-sm-12"><div class="panel panel-default"><div class="panel-heading">Editor</div><div class="panel-body chap-config"></div></div></div></div><div class="tab-pane row info" id="info"><div class="col-sm-6"><label>Title</label><input type="text" name="title" class="form-control"></div><div class="col-sm-6"><label>Sub Title</label><input type="text" name="subtitle" class="form-control"></div><div class="col-sm-6"><label>Status</label><input type="text" name="status" class="form-control"></div><div class="col-sm-6"><label>Thời lượng</label><input type="text" name="length" class="form-control"></div><div class="col-sm-6"><label>Đạo diễn</label><input type="text" name="director" class="form-control"></div><div class="col-sm-6"><label>Quốc gia</label><input type="text" name="country" class="form-control"></div><div class="col-sm-6"><label>Năm phát hành</label><input type="text" name="year" class="form-control"></div><div class="col-sm-6"><label>Thể loại</label><textarea class="form-control" name="category" rows="3"></textarea></div><div class="col-sm-6"><label>Diễn viên</label><textarea class="form-control" name="stars" rows="3"></textarea></div><div class="col-sm-6"><label>Nguồn</label><textarea class="form-control" name="source" rows="3"></textarea></div><div class="col-sm-6"><label>Giới thiệu</label><textarea class="form-control" name="descript_long" rows="10"></textarea></div><div class="col-sm-6"><label>Giới thiệu Ngắn</label><textarea class="form-control" name="descript_short" rows="10"></textarea></div></div></div>');
					
					///// insert info /////
					var menu 	= form.find('.menu:first');
					menu.affix({
						offset: {
							top: 200
						}
					});
					// all chaps information
					$.each(result['post']['chaps'], function(i, chap){
						var mv_found 	= false;
						for (var i = 0; i < result['post']['movie'].length; i++) {
							var mv 	= result['post']['movie'][i];
							if (mv['id'].length > 0 && mv['id'] == chap['id']) {
								mv['server'] = chap['server'];
								mv_found 	= true;
								break;
							};
						};
						if (!mv_found) {
							chap['id'] 	= '';
							chap['name'] = 'unknown';
							result['post']['movie'].push(chap);
						};
					});
					// list chap in movie
					var f_chaps 	= form.find('.chaps');
					$.each(result['post']['movie'], function(i, chap){
						self._Chap_Json2Obj(chap).appendTo(f_chaps);
					});
					// movie information
					console.debug(result['post']);
					for (var k in result['post']) {
						if (k != "movie" && k != "chaps"){
							var obj 	= form.find('.tab-pane [name='+k+']');
							if (obj.length > 0) {
								data 	= result['post'][k];
								if ($.type(data) == "array") {
									data 	= data.join('\n');
								}else if($.type(data) == "object") {
									data 	= JSON.stringify(data);
								};
								obj.val(data);
							};
						};
					};
					// insert modal
					self.modal_title.html("Edit Movie");
					self.modal_body.html(form);
					self.modal_footer.html('<button type="button" class="btn btn-warning btn-edit" data-dismiss="modal">Save</button><button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

					self.modal_object 	= post;
					self.modal.modal('show');
				};
			}
		});
		// self.app._ProcessBar.Reset();
		// self.app._ProcessBar.Run(50);
		// PageAjax({
		// 	type: "post",
		// 	dataType: "json",
		// 	url: window.location.href,
		// 	data: query
		// }).done(function(result) {
		// 	self.app._ProcessBar.Run(100);
		// 	if (result['post'] != undefined) {
		// 		var form 	= $('<ul class="nav nav-tabs" role="tablist"><li class="active"><a href="#movie" role="tab" data-toggle="tab">Movie</a></li><li><a href="#info" role="tab" data-toggle="tab">Profile</a></li></ul><div class="tab-content edit-post"><div class="tab-pane row active movie" id="movie"><div class="col-sm-12"><div class="row menu"><div class="col-sm-6"><label>Chap</label><div class="btn-toolbar" role="toolbar"><div class="btn-group"><button type="button" title="Edit Chap" class="btn btn-group-sm btn-primary btn-chap-edit"><span class="glyphicon glyphicon-edit"></span></button><button type="button" title="Append Chap" class="btn btn-group-sm btn-success btn-chap-append"><span class="glyphicon glyphicon-plus"></span></button></div><div class="btn-group"><button type="button" title="Move Chap Up" class="btn btn-group-sm btn-info btn-chap-up"><span class="glyphicon glyphicon-circle-arrow-up"></span></button><button type="button" title="Move Chap Down" class="btn btn-group-sm btn-warning btn-chap-down"><span class="glyphicon glyphicon-circle-arrow-down"></span></button></div><div class="btn-group"><button type="button" title="Remove Chap" class="btn btn-group-sm btn-danger btn-chap-remove"><span class="glyphicon glyphicon-trash"></span></button></div></div></div><div class="col-sm-6"><label>Server</label><div class="btn-toolbar" role="toolbar"><div class="btn-group"><button type="button" class="btn btn-group-sm btn-primary btn-srv-edit"><span class="glyphicon glyphicon-edit"></span></button><button type="button" class="btn btn-group-sm btn-success btn-srv-append"><span class="glyphicon glyphicon-plus"></span></button></div><div class="btn-group"><button type="button" class="btn btn-group-sm btn-info btn-srv-left"><span class="glyphicon glyphicon-circle-arrow-left"></span></button><button type="button" class="btn btn-group-sm btn-warning btn-srv-right"><span class="glyphicon glyphicon-circle-arrow-right"></span></button></div><div class="btn-group"><button type="button" class="btn btn-group-sm btn-danger btn-srv-remove"><span class="glyphicon glyphicon-trash"></span></button></div></div></div></div><div class="row inset select chaps"></div></div><div class="col-sm-12"><div class="panel panel-default"><div class="panel-heading">Editor</div><div class="panel-body chap-config"></div></div></div></div><div class="tab-pane row info" id="info"><div class="col-sm-6"><label>Title</label><input type="text" name="title" class="form-control"></div><div class="col-sm-6"><label>Sub Title</label><input type="text" name="subtitle" class="form-control"></div><div class="col-sm-6"><label>Status</label><input type="text" name="status" class="form-control"></div><div class="col-sm-6"><label>Thời lượng</label><input type="text" name="length" class="form-control"></div><div class="col-sm-6"><label>Đạo diễn</label><input type="text" name="director" class="form-control"></div><div class="col-sm-6"><label>Quốc gia</label><input type="text" name="country" class="form-control"></div><div class="col-sm-6"><label>Năm phát hành</label><input type="text" name="year" class="form-control"></div><div class="col-sm-6"><label>Thể loại</label><textarea class="form-control" name="category" rows="3"></textarea></div><div class="col-sm-6"><label>Diễn viên</label><textarea class="form-control" name="stars" rows="3"></textarea></div><div class="col-sm-6"><label>Nguồn</label><textarea class="form-control" name="source" rows="3"></textarea></div><div class="col-sm-6"><label>Giới thiệu</label><textarea class="form-control" name="descript_long" rows="10"></textarea></div><div class="col-sm-6"><label>Giới thiệu Ngắn</label><textarea class="form-control" name="descript_short" rows="10"></textarea></div></div></div>');
				
		// 		///// insert info /////
		// 		var menu 	= form.find('.menu:first');
		// 		menu.affix({
		// 			offset: {
		// 				top: 200
		// 			}
		// 		});
		// 		// all chaps information
		// 		$.each(result['post']['chaps'], function(i, chap){
		// 			var mv_found 	= false;
		// 			for (var i = 0; i < result['post']['movie'].length; i++) {
		// 				var mv 	= result['post']['movie'][i];
		// 				if (mv['id'].length > 0 && mv['id'] == chap['id']) {
		// 					mv['server'] = chap['server'];
		// 					mv_found 	= true;
		// 					break;
		// 				};
		// 			};
		// 			if (!mv_found) {
		// 				chap['id'] 	= '';
		// 				chap['name'] = 'unknown';
		// 				result['post']['movie'].push(chap);
		// 			};
		// 		});
		// 		// list chap in movie
		// 		var f_chaps 	= form.find('.chaps');
		// 		$.each(result['post']['movie'], function(i, chap){
		// 			self._Chap_Json2Obj(chap).appendTo(f_chaps);
		// 		});
		// 		// movie information
		// 		console.debug(result['post']);
		// 		for (var k in result['post']) {
		// 			if (k != "movie" && k != "chaps"){
		// 				var obj 	= form.find('.tab-pane [name='+k+']');
		// 				if (obj.length > 0) {
		// 					data 	= result['post'][k];
		// 					if ($.type(data) == "array") {
		// 						data 	= data.join('\n');
		// 					}else if($.type(data) == "object") {
		// 						data 	= JSON.stringify(data);
		// 					};
		// 					obj.val(data);
		// 				};
		// 			};
		// 		};
		// 		// insert modal
		// 		self.modal_title.html("Edit Movie");
		// 		self.modal_body.html(form);
		// 		self.modal_footer.html('<button type="button" class="btn btn-warning btn-edit" data-dismiss="modal">Save</button><button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

		// 		self.modal_object 	= post;
		// 		self.modal.modal('show');
		// 	};
		// }).error(function(e){
		// 	console.error(e);
		// });
		event.preventDefault();
		event.stopPropagation();
	});
	// edit action
	this.modal.on('click', '.modal-footer .btn.btn-edit', function(event) {
		var query 		= {'is':'edit'};
		var args 		= self.modal_body.find('.tab-pane.info [name]');
		$.each(args, function(i, v){
			var obj 	= $(v);
			var name 	= obj.attr('name');
			var data 	= obj.val();
			query['p_'+name] 	= data;
		});
		var chaps 			= self.modal_body.find('.tab-pane.movie .chaps .chap');
		query['p_movie'] 	= JSON.stringify(self._Chaps_Obj2Json(chaps));
		self.ManagerPost(self.modal_object, query);
	});
	// event chap edit
	self.modal.on('click', '.edit-post .menu .btn-chap-edit', function(event){
		var chaps 		= self.modal.find('.edit-post .chaps');
		var selected 	= chaps.children('.chap.active');
		if (selected.length > 0) {
			chaps.scrollTop(selected.position().top + chaps.scrollTop() - 150);
			var config 		= self.modal.find('.edit-post .chap-config:first').html('<div class="row chap-editor"><div class="col-xs-12"><label>Chap Name</label><input type="text" class="form-control chap-name" placeholder="chap name"></div><div class="col-xs-12"><label>Chap JSON</label><textarea class="form-control chap-json" placeholder="chap name"></textarea></div><div class="col-xs-6 col-xs-offset-3"><div class="btn btn-primary chap-update">Update</div><div class="btn btn-success chap-close">Close</div></div></div>');

			var chap_json 	= self._Chap_Obj2Json(selected);
			// change name -> change config
			var chap_name_obj 		= config.find('.chap-name:first');
			var chap_json_obj 		= config.find('.chap-json:first');
			var _Chap_Update_Data 	= function(){
				chap_name_obj.val(chap_json['name']);
				chap_json_obj.val(js_beautify(JSON.stringify(chap_json),{
					'indent_size': 1,
					'indent_char': '\t'
				}));
			};
			_Chap_Update_Data();
			// event
			chap_name_obj.bind('change', function(event){
				chap_json['name'] 	= $(this).val();
				_Chap_Update_Data();
			});
			chap_json_obj.bind('change', function(event){
				chap_json 	= JSON.parse($(this).val());
				_Chap_Update_Data();
			});
			// update chap
			config.find('.btn.chap-update').bind('click', function(event){
				console.debug(chap_json);
				var new_obj = self._Chap_Json2Obj(chap_json).insertAfter(selected).addClass('active');
				selected.remove();
				selected = new_obj;
			});
		}else{
			alert('plz select one chap!');
		};
	});
	// event chap append
	self.modal.on('click', '.edit-post .menu .btn-chap-append', function(event){
		var chaps 		= self.modal.find('.edit-post .chaps');
		var selected 	= chaps.children('.chap.active');
		var new_obj 	= self._Chap_Json2Obj({});
		if (selected.length > 0) {
			selected.after(new_obj);
		}else{
			chaps.append(new_obj);
		};
		new_obj.click();
		self.modal.find('.edit-post .menu .btn-chap-edit').click();
	});
	// event chap up
	self.modal.on('click', '.edit-post .menu .btn-chap-up', function(event){
		var selected 	= self.modal.find('.edit-post .chaps .chap.active');
		if (selected.length > 0) {
			var before 	= selected.prev();
			if (before.length > 0) {
				before.before(selected.detach());
			};
		};
	});
	// event chap up
	self.modal.on('click', '.edit-post .menu .btn-chap-down', function(event){
		var selected 	= self.modal.find('.edit-post .chaps .chap.active');
		if (selected.length > 0) {
			var after 	= selected.next();
			if (after.length > 0) {
				after.after(selected.detach());
			};
		};
	});
	self.modal.on('click', '.edit-post .menu .btn-chap-remove', function(event){
		var selected 	= self.modal.find('.edit-post .chaps .chap.active');
		if (selected.length > 0) {
			if (confirm('Are you sure you want to remove selected chap?')) {
				selected.remove();
			};
		};
	});
	//////
	var _Modal_Edit_Chap_Select  = function(){
		// clear update chap/server form
		self.modal.find('.edit-post .chap-config:first').children().hide();
	};
	// event click chap
	self.modal.on('click', '.edit-post .chap', function(event){
		var obj 	= $(this);
		if (!obj.hasClass('active')) {
			obj.parent().find('.chap.active, .chap .srv.active').removeClass('active');
			obj.addClass('active');
			_Modal_Edit_Chap_Select();
		};
		event.preventDefault();
		event.stopPropagation();
	});
	// show server name/server/parts config
	self.modal.on('click', '.edit-post .chap .srvs .srv', function(event){
		var obj 	= $(this);
		if (!obj.hasClass('active')) {
			self.modal.find('.edit-post .chap.active, .edit-post .chap .srv.active').removeClass('active');
			obj.addClass('active');
			obj.parents('.chap:first').addClass('active');
			_Modal_Edit_Chap_Select();
		};
		event.preventDefault();
		event.stopPropagation();
	});
	//////////////// edit server modal event
	self.modal.on('click', '.edit-post .menu .btn-srv-edit', function(event){
		var chaps 			= self.modal.find('.edit-post .chaps');
		var chap_selected 	= chaps.children('.chap.active');
		var srv_selected 	= chap_selected.find('.srv.active');
		if (srv_selected.length > 0) {
			chaps.scrollTop(chap_selected.position().top + chaps.scrollTop() - 150);
			var config 		= self.modal.find('.edit-post .chap-config:first').html('<div class="row srv-editor"><div class="col-xs-12"><label>JSON</label><textarea class="form-control srv-json" placeholder="server json"></textarea></div><div class="col-xs-12"><label>Name</label><input type="text" class="form-control srv-name" placeholder="server name"></div><div class="col-xs-12"><label>Parts</label><div class="row part-edit"><ul class="col-xs-4 inset parts"><li class="part">1-a</li><li class="part">1-b</li></ul><div class="col-xs-8 part-editor"><label>Name</label><input type="text" class="form-control part-name" placeholder="part name"><label>Link</label><input type="text" class="form-control part-link" placeholder="part link"><label>Source</label><textarea class="form-control part-source" placeholder="part source"></textarea><label>JSON</label><textarea class="form-control part-json" placeholder="part json"></textarea></div></div></div><div class="col-xs-6 col-xs-offset-3"><div class="btn btn-primary srv-update">Update</div><div class="btn btn-success srv-close">Close</div></div></div>');

			var srv_json 	= self._Server_Obj2Json(srv_selected);
			// console.debug(js_beautify(srv_json));
			// change name -> change config
			var srv_name_obj 		= config.find('.srv-name:first');
			var srv_json_obj 		= config.find('.srv-json:first');
			var srv_parts_obj 		= config.find('.part-edit .parts:first');
			var _Srv_Update_Data 	= function(){
				srv_name_obj.val(srv_json['name']);
				srv_json_obj.val(js_beautify(JSON.stringify(srv_json),{
					'indent_size': 1,
					'indent_char': '\t'
				}));
				srv_parts_obj.html('');
				for (var i = 0; i < srv_json['part'].length; i++) {
					var part 		= srv_json['part'][i];
					var part_obj 	= $('<li class="part" data="'+Base64.encode(JSON.stringify(part))+'">'+part['name']+'</li>');
					srv_parts_obj.append(part_obj)
				};
			};
			_Srv_Update_Data();
			// event
			srv_name_obj.bind('change', function(event){
				srv_json['name'] 	= $(this).val();
				_Srv_Update_Data();
			});
			srv_json_obj.bind('change', function(event){
				srv_json 	= JSON.parse($(this).val());
				_Srv_Update_Data();
			});
			srv_parts_obj.on('click','.part', function(event){
				var part_json 	= JSON.parse(Base64.decode($(this).attr('data')));
				config.find('.part-edit .part-editor .part-json').val(js_beautify(part_json));
				_Srv_Update_Data();
			});
			// update chap
			config.find('.btn.srv-update').bind('click', function(event){
				console.debug(srv_json);
				var new_obj = self._Server_Json2Obj(srv_json).insertAfter(srv_selected).addClass('active');
				srv_selected.remove();
				srv_selected = new_obj;
			});
		}else{
			alert('plz select one server!');
		};
	});
	// event server append
	self.modal.on('click', '.edit-post .menu .btn-srv-append', function(event){
		var chap 		= self.modal.find('.edit-post .chaps .chap.active .srvs>ul');
		var selected 	= chap.find('.srv.active');
		var new_obj 	= self._Server_Json2Obj({});
		if (selected.length > 0) {
			selected.after(new_obj);
		}else{
			chap.append(new_obj);
		};
		new_obj.click();
		self.modal.find('.edit-post .menu .btn-srv-edit').click();
	});
	// event server up
	self.modal.on('click', '.edit-post .menu .btn-srv-left', function(event){
		var selected 	= self.modal.find('.edit-post .chap.active .srv.active');
		if (selected.length > 0) {
			var before 	= selected.prev();
			if (before.length > 0) {
				before.before(selected.detach());
			};
		};
	});
	// event server up
	self.modal.on('click', '.edit-post .menu .btn-srv-right', function(event){
		var selected 	= self.modal.find('.edit-post .chap.active .srv.active');
		if (selected.length > 0) {
			var after 	= selected.next();
			if (after.length > 0) {
				after.after(selected.detach());
			};
		};
	});
	// remove server
	self.modal.on('click', '.edit-post .menu .btn-srv-remove', function(event){
		var selected 	= self.modal.find('.edit-post .chap.active .srv.active');
		if (selected.length > 0) {
			if (confirm('Are you sure you want to remove selected server ?')) {
				selected.remove();
			};
		};
	});
	////////////delete post
	this.form.on('click', '.post .manager .delete', function(event){
		var obj 		= $(this);
		// self.ManagerPost(obj.parents('.post:first'), {'is':'restore'});
		self.modal_title.html("Restore post");
		self.modal_body.html('Delete this box?');
		self.modal_footer.html('<button type="button" class="btn btn-danger btn-delete" data-dismiss="modal">Delete</button><button type="button" class="btn btn-default btn-close" data-dismiss="modal">Close</button>');

		self.modal_object 	= obj.parents('.post:first');
		self.modal.modal('show');
		event.preventDefault();
		event.stopPropagation();
	});
	// delete action
	this.modal.on('click', '.modal-footer .btn.btn-delete', function(event) {
		self.ManagerPost(self.modal_object, {'is':'delete'});
	});
};
PageModuleCineManager.prototype._Chaps_Obj2Json = function(chaps){
	var self 	= this;
	var result 	= [];
	$.each(chaps, function(i, v){
		var chap = $(v);
		result.push(self._Chap_Obj2Json(chap));
	});
	return result;
};
PageModuleCineManager.prototype._Chap_Json2Obj = function(chap){
	var self 		= this;
	if (chap['name'] == undefined) {
		chap['name'] 	= 'unknown';
	};
	if (chap['id'] == undefined) {
		chap['id'] 		= '';
	};
	if (chap['server'] == undefined) {
		chap['server'] 	= [];
	};
	//
	f_chap 			= $('<div class="option chap row" chap-id="'+chap['id']+'" chap-name="'+chap['name']+'">'+
							'<div class="col-xs-2 name">'+chap['name']+'</div>'+
							'<div class="col-xs-10 srvs"><ul></ul></div>'+
						'</div>');
	var f_srvs 		= f_chap.find('.srvs>ul');
	$.each(chap['server'], function(i, srv){
		f_srvs.append(self._Server_Json2Obj(srv));
	});
	// f_chap.attr('data', Base64.encode(JSON.stringify(chap)));
	return f_chap;
};
PageModuleCineManager.prototype._Chap_Obj2Json = function(chap){
	var self 		= this;
	var chap_json 	= {
		"id"		: chap.attr('chap-id'),
		"name"		: chap.attr('chap-name'),
		"server"	: []
	};
	var srvs 		= chap.find('.srv');
	$.each(srvs, function(i, v){
		var srv 	= $(v);
		chap_json['server'].push(self._Server_Obj2Json(srv));
	});
	return chap_json;
};
PageModuleCineManager.prototype._Server_Json2Obj = function(srv){
	if (srv['name'] == undefined) {
		srv['name'] = 'unknown';
	};
	if (srv['part'] == undefined) {
		srv['part'] = [];
	};
	var f_srv 	= ""
	$.each(srv['part'], function(i, part){
		f_srv 	+= '<li class="part">'+part['name']+'</li>';
	});
	f_srv 	= '<li class="col-sm-4 srv" data="'+Base64.encode(JSON.stringify(srv))+'">'+
				'<div class="row"><div class="col-xs-4">Name : </div><div class="col-xs-8 srv-name">'+srv['name']+'</div></div>'+
				'<div class="row srv-parts"><ul>'+f_srv+'</ul></div>'+
			'</li>';
	return $(f_srv);
};
PageModuleCineManager.prototype._Server_Obj2Json = function(srv){
	return JSON.parse(Base64.decode(srv.attr('data')));
};

PageModuleCineManager.prototype.ManagerPost = function(post, query){
	var self 	= this;
	query['action']		= "manager";
	query['module'] 	= self.form.attr('module-id');
	query['post'] 		= post.attr('post-id');

	console.debug(query);

	self.Load({
		"query": query,
		"callback": function(result) {
			if (result['error'] == 0) {
				var mng 	= post.find('.manager');
				// if (query['is'] == "trash" || query['is'] == "restore") {
				if (query['is'] == "trash" || query['is'] == "restore" || query['is'] == "delete") {
					post.remove();
				}else if (query['is'] == "public" || query['is'] == "private") {
					mng.children().removeAttr('disabled');
					post.removeClass('public private').addClass(query['is']);
				};
			};
		}
	});
	// self.app._ProcessBar.Reset();
	// self.app._ProcessBar.Run(50);
	// PageAjax({
	// 	type: "post",
	// 	dataType: "json",
	// 	url: window.location.href,
	// 	data: query
	// }).done(function(result) {
	// 	self.app._ProcessBar.Run(100);
	// 	if (result['error'] == 0) {
	// 		var mng 	= post.find('.manager');
	// 		// if (query['is'] == "trash" || query['is'] == "restore") {
	// 		if (query['is'] == "trash" || query['is'] == "restore" || query['is'] == "delete") {
	// 			post.remove();
	// 		}else if (query['is'] == "public" || query['is'] == "private") {
	// 			mng.children().removeAttr('disabled');
	// 			post.removeClass('public private').addClass(query['is']);
	// 		};
	// 	};
	// }).error(function(e){
	// 	console.error(e);
	// });
};
PageModuleCineManager.prototype.Refesh = function() {
	Module.prototype.Refesh.call(this);
	var self 	= this;

	// view user info
	if (typeof(self.setting['user']) != "undefined") {
		var obj = self.form.find('.post .user .by');
		if (self.setting['user']) {
			obj.show();
		}else{
			obj.hide();
		};
	};
	// update blank
	if (typeof(self.setting['blank']) != "undefined" && self.setting['blank']) {
		var posts 	= self.form.find('.posts .post');
		$.each(posts, function(key, value){
			var obj = $(value);
			if (!obj.data('md-blanked')) {
				obj.find('.image a').attr('target', '_blank');
				obj.find('.title a').attr('target', '_blank');
				obj.data('md-blanked', true);
			};
		});
	}else{
		self.form.find('.post .image a:not([site-goto]), .post .title a:not([site-goto])').attr('site-goto', '+');
	}
	/////
	var update_fb_info 	= false;
	// view button
	if (typeof(self.setting['view']) != "undefined" && self.setting['view']) {
		self.form.find('.post .user .info .view').show();
	};
	// like button
	if (typeof(self.setting['like']) != "undefined" && self.setting['like']) {
		self.form.find('.post .user .info .like').show();
		update_fb_info 		= true;
	};
	// share button
	if (typeof(self.setting['share']) != "undefined" && self.setting['share']) {
		self.form.find('.post .user .info .share').show();
		update_fb_info 		= true;
	};
	// comment button
	if (typeof(self.setting['comment']) != "undefined" && self.setting['comment']) {
		self.form.find('.post .user .info .comment').show();
		update_fb_info 		= true;
	};
	if (update_fb_info) {
		var posts 	= self.form.find('.posts .post');
		$.each(posts, function(key, value){
			var obj = $(value);
			if (!obj.data('md-fb-info-updated')) {
				var link 	= obj.find('.title a:first')[0].href;
				$.getJSON("http://graph.facebook.com/?id=" + link, function(data){
				// $.getJSON("http://graph.facebook.com/?id=https://www.facebook.com/", function(data){
					obj.find('.info .like:first').append(typeof(data['likes']) != "undefined" ? data['likes']: 0);
					obj.find('.info .comment:first').append(typeof(data['comments']) != "undefined" ? data['comments']: 0);
					obj.find('.info .share:first').append(typeof(data['shares']) != "undefined" ? data['shares']: 0);
				});
				obj.data('md-fb-info-updated', true);
			};
		});
	};
	// view more button
	if (typeof(self.setting['more']) != "undefined") {
		var more = self.form.find('.footer .view-more');
		if (!more.data('md-mored')) {
			if (self.setting['more']) {
				more.show();
			}else{
				more.hide();
			};
			more.data('md-mored', true);
		};
	};
	// update height
	if (typeof(self.setting['max-height']) == "number") {
		if (self.setting['max-height'] > 0) {
			var obj = self.form.find('.main:first');
			if (!obj.data('md-heighted')) {
				obj.css("max-height", self.setting['max-height']+ "vh");
				obj.data('md-heighted', true);
			};
		};
	};
};