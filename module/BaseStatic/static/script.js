var PageModuleBaseStatic=function(a){this.app=a;this.setting={"class":{},header:!0};this.template={}};
PageModuleBaseStatic.prototype={Description:function(){return this.descript=$("<h3>module PageModuleBaseStatic</3></h4>module duoc dung de show cac bai post, anh, duong dan den cac bai post ...</h4>")},Init:function(a){if("undefined"==typeof this.inited)this.inited=!0;else return!0;this.form=a;this.posts=this.form.find(".main .posts:first");a=JSON.parse(Base64.decode(this.form.attr("module-setting")));for(var b in a)this.setting[b]=a[b];this.template.post=Base64.decode(this.form.attr("module-template"))},
Refesh:function(){var a=this;"undefined"!=typeof a.setting["class"]&&$.each(a.setting["class"],function(b,d){var e=a.form.find("."+b);$.each(e,function(a,b){var c=$(b);c.data("md-classed")||c.addClass(d).data("md-classed",!0)})});if("undefined"!=typeof a.setting.header){var b=a.form.find(".main:first .header:first");a.setting.header?b.show():b.hide()}}};