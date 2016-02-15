(function($) {
	$.fn.MediaPlayer = function(opt) {

		opt = $.extend({
			list: [],
			handle:"",
			autoplay: false,
			preload: true,
			chunks: 3,
			chunksWait: 60,
			chunksStep: 512000,
			onLoad: undefined,
			onEnded: undefined,
			onBuffer: undefined,
			onError: undefined,
			onSeeked: undefined,
			onSeeking: undefined,
			onVolumeChange: undefined
		}, opt);

		// limit chunks
		opt.chunks = Math.min(16, Math.max(1, opt.chunks));

		if(opt.handle === "") {
			var $el = this;
		} else {
			var $el = this.find(opt.handle);
		}

		// clear container
		var video_container = $('<div class="videos" style="position: relative;"></div>')
		$el.html(video_container);

		var current_video_index = 0;
		for (var i in opt.list) {
			if (opt.list[i].default == true) {
				current_video_index = i;
				break;
			};
		};

		var current_video = opt.list[current_video_index];
		var video_info 	= {
			duration: 0,
			speed: 0.01,
			bytepertime: 0,
			endTime: 0,
			runningTime: 0,
			chunking: 0
		}


		var __MakeVideosMp4 = function(source, bytes){
			// load first chunks for information
			var startTime = parseInt(Date.now()/1000);
			var endTime = startTime;
			// var video = $('<video autoplay muted style="position: absolute;width: 100%;z-index: -1;opacity: 0;" preload="metadata"></video>');
			var video = $('<video controls muted width="100%" preload="auto"></video>');
			// var video = $('<video controls autoplay loop muted style="position: absolute;width: 100%;z-index: -1;opacity: 0;" preload="auto"></video>');
			video.bind('loadedmetadata', function(event){
				console.debug('video loadedmetadata', this, event, this.duration);
				video_info.duration = this.duration;

			});
			video.bind('timeupdate', function(event){
				// console.debug('video time', this.currentTime);
				if (this.currentTime > 0 && this.currentTime < video_info.duration) {
					video_info.endTime = this.currentTime;
				};
				if (this.currentTime >= 59) {
					this.currentTime = 55;
				};
			});
			// video.bind('pause', function(event){
			// 	console.debug('buffered', this.buffered)
			// 	for (var i = 0; i < this.buffered.length; i++) {
			// 		console.debug('buffered step', i, this.buffered.start(i), this.buffered.end(i))
			// 	};
			// 	// console.debug(this.buffered.length, this.buffered.start(this.buffered.length -1))
			// 	this.currentTime = this.buffered.start(this.buffered.length -1);
			// });
			// video.bind('seeked', function(event){
			// 	// console.debug('buffered', this.buffered)
			// 	this.play();
			// });
			
			video.bind('progress', function(event){
				console.debug('buffered', this.buffered.end(this.buffered.length -1));
				// if (this.buffered.length == 0) {return};
				// var buffered_end = this.buffered.end(0);
				// if (buffered_end > 0 && buffered_end < video_info.duration) {
				// 	endTime = parseInt(Date.now()/1000);
				// 	// console.debug('speed end time', endTime);
				// };

			});
			video.one('ended', function(event){
				// speed
				console.debug('inited',endTime ,startTime);
				video_info.speed = bytes/(endTime - startTime);
				// -350 byte info start
				video_info.bytepertime = 200000//(bytes - 250000)/video_info.endTime;
				console.debug('video_info', video_info)
				// video.attr('data-start-bytes', 0);
				// video.attr('data-end-bytes', bytes);
				// video.attr('data-start-time', 0);
				// video.attr('data-end-time', video_info.endTime);

				this.pause();
				// video.remove();
				// __MakeVideosMp4Chunks(source, opt.chunksWait); // load video buffer in 15s
			});
			var url = source.url +"#t=50,60"//+ "&range=0-" + bytes;
			video.append('<source src="'+url+'" type="'+source.type+'" />');
			video.appendTo(video_container);
			// video[0].src = url;
		};
		var __MakeVideosMp4Chunks = function(source, loadtime){
			while(opt.chunks > video_info.chunking){
				video_info.chunking++;
				__MakeVideosMp4NextChunk(source, loadtime);
			}
		};
		var __MakeVideosMp4NextChunk = function(source, loadtime){
			var lastvideo = video_container.find('video:last');
			if (lastvideo.length == 0) {
				var starttime = 0;
				var startbytes = 0;
			}else{
				var starttime = parseFloat(lastvideo.data('end-time'));
				var startbytes = parseFloat(lastvideo.data('end-bytes'));
			};
			
			// tinh thoi gian load video 
			// tu luc video dang chay den khi video chay den doan chunk nay
			if(!loadtime){
				loadtime = starttime - video_info.runningTime;
			}
			// so bytes can load trong 15s + so byte cua lash video
			endbytes = parseInt((loadtime)*video_info.speed/opt.chunks + startbytes);
			if (starttime == 0) {
				endbytes = endbytes + 200000;
			};
			endtime = starttime + (endbytes - startbytes)/video_info.bytepertime;
			console.debug('chunk ', starttime, endtime, startbytes, endbytes)

			// 
			// var video = $('<video autoplay muted preload="metadata" style="position: absolute;width: 100%;z-index: -1;opacity: 0;"></video>');
			var video = $('<video controls loop autoplay muted width="50%" style="float: left;" preload="none"></video>');
			// var video = $('<video controls autoplay loop muted style="position: absolute;width: 100%;z-index: -1;opacity: 0;" preload="auto"></video>');
			video.attr('data-start-bytes', startbytes);
			video.attr('data-end-bytes', endbytes);
			video.attr('data-start-time', starttime);
			video.attr('data-end-time', endtime);

			// event
			video.bind('loadedmetadata', function(event){
				console.debug('video loadedmetadata', this, event);
				// seek to before start 0.3s for block video pass
				// this.currentTime = starttime - 0.3;
				console.debug('video seek ', starttime);

				// var seektime = (startbytes/endbytes)*video_info.duration;
				// console.debug('seektime', seektime)
				this.currentTime = starttime - 0.6;
			});

			// video.bind('timeupdate', function(event){
			// 	console.debug('video time', this.currentTime);
			// });
			// var seeked = false;
			var played = false;
			video.bind('progress', function(event){
				var length = this.buffered.length;
				if (length == 0) {return};
				// console.debug(length, this.buffered.start(length -1), this.buffered.end(length -1))

				// if (this.buffered.end(0) >= endtime - 0.3) {
				// 	this.pause();
				// 	this.currentTime = starttime;

				// 	video_info.chunking--;

				// 	if (video_info.chunking == 0) {
				// 		__VideoPlayerNext();
				// 	};
				// };

				// finished
				if (this.buffered.end(length - 1) >= video_info.duration) {
					// this.currentTime = starttime;
					this.pause();
					video_info.chunking--;
					console.debug('buffered', video_info.chunking)
					if (video_info.chunking == 0 && !played) {
						__VideoPlayerNext();
						played = true;
					};
					video.unbind('progress');
				};
			});

			var url = source.url + "&range=0-" + endbytes;
			video.append('<source src="'+url+'" type="'+source.type+'" />');
			video.appendTo(video_container);
		};

		var __VideoPlayerNext = function(startTime){
			console.debug('call player');
			var oldvideo = video_container.find('video.playing:first');
			var video = oldvideo.next(':first');
			if (oldvideo.length == 0) {
				video = video_container.find('video:first');
			};
			if (video.length == 0) {return;};
			console.debug(video);
			// unblind all event
			video.unbind('loadedmetadata progress timeupdate ended');
			// new event
			var endTime = parseFloat(video.data('end-time'));
			video.bind('timeupdate', function(event){
				if (this.currentTime >= endTime - 0.3) {
					console.debug('video end chunk at ', this.currentTime);
					this.pause();
					__VideoPlayerNext(this.currentTime);
				};
			});
			oldvideo.css({
				// 'opacity': 0,
				// 'z-index': -1
			}).removeClass('playing');
			video.css({
				// 'opacity': 1,
				// 'z-index': 1
			}).addClass('playing');

			if (!startTime) {
				startTime = 0;
			};
			video[0].muted = false;
			if (startTime > endTime) {
				video[0].currentTime = startTime;
			};
			video[0].play();
		};
		// first chunks info
		if (current_video.type == 'video/mp4') {
			__MakeVideosMp4(current_video, opt.chunksStep);
		};

		

		return $el;
	}
})(jQuery);