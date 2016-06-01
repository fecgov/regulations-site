'use strict';

var $ = require('jquery');
var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var MainEvents = require('../../events/main-events');
var CommentEvents = require('../../events/comment-events');
var comments = require('../../collections/comment-collection');

var CommentConfirmView = Backbone.View.extend({
  initialize: function(options) {
    Backbone.View.prototype.setElement.call(this, '#' + options.id);

    this.docId = this.$el.data('doc-id');
    this.metadataUrl = this.$el.data('metadata-url');

    if (this.metadataUrl) {
      this.poll(this.metadataUrl);
      comments.filter(this.docId).forEach(function(comment) {
        comment.destroy();
      });
    }
  },

  poll: function(url) {
    this.interval = window.setInterval(
      function() {
        $.getJSON(url).then(function(resp) {
          this.setPdfUrl(resp.pdfUrl);
          if (resp.trackingNumber) {
            this.setTrackingNumber(resp.trackingNumber);
            window.clearInterval(this.interval);
          }
        }.bind(this));
      }.bind(this),
      5000
    );
  },

  /**
   * Fill in an element's (indicated by the selector) template with the ctx
   * provided
   **/
  replaceTemplate: function(selector, ctx) {
    this.$el.find(selector).each(function(idx, elt) {
      var $elt = $(elt);
      var $tplElt = $elt.find('.js-template');
      var result = _.template($tplElt.prop('innerHTML'))(ctx);
      $elt.empty();
      $elt.append($tplElt);
      $elt.append(result);
    });
  },

  setPdfUrl: function(url) {
    this.replaceTemplate('.save-pdf', {url: url});
  },

  setTrackingNumber: function(number) {
    this.replaceTemplate('.tracking-number .status', {number: number});
  }
});

module.exports = CommentConfirmView;
