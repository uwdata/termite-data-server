(function(exports) {
	var topicWidth = 225,
	topicHeight = 225,
	margin = 10,
	header = 60,
	left = 20;

	var twentytopiclayout = [];

	twentytopiclayout[16] = {"left":left, "top":header};
	twentytopiclayout[8] = {"left":left + topicWidth + margin, "top":header};
	twentytopiclayout[6] = {"left":left + 2*(topicWidth + margin), "top":header};
	twentytopiclayout[7] = {"left":left + 3*(topicWidth + margin), "top":header};
	twentytopiclayout[17] = {"left":left + 4*(topicWidth + margin), "top":header};

	twentytopiclayout[12] = {"left":left, "top":header + (topicHeight + margin)};
	twentytopiclayout[2] = {"left":left + (topicWidth + margin), "top":header + (topicHeight + margin)};
	twentytopiclayout[0] = {"left":left + 2*(topicWidth + margin), "top":header + (topicHeight + margin)};
	twentytopiclayout[3] = {"left":left + 3*(topicWidth + margin), "top":header + (topicHeight + margin)};
	twentytopiclayout[14] = {"left":left + 4*(topicWidth + margin), "top":header + (topicHeight + margin)};

	twentytopiclayout[13] = {"left":left, "top":header + 2*(topicHeight + margin)};
	twentytopiclayout[5] = {"left":left + (topicWidth + margin), "top":header + 2*(topicHeight + margin)};
	twentytopiclayout[1] = {"left":left + 2*(topicWidth + margin), "top":header + 2*(topicHeight + margin)};
	twentytopiclayout[4] = {"left":left + 3*(topicWidth + margin), "top":header + 2*(topicHeight + margin)};
	twentytopiclayout[15] = {"left":left + 4*(topicWidth + margin), "top":header + 2*(topicHeight + margin)};

	twentytopiclayout[18] = {"left":left, "top":header + 3*(topicHeight + margin)};
	twentytopiclayout[10] = {"left":left + (topicWidth + margin), "top":header + 3*(topicHeight + margin)};
	twentytopiclayout[9] = {"left":left + 2*(topicWidth + margin), "top":header + 3*(topicHeight + margin)};
	twentytopiclayout[11] = {"left":left + 3*(topicWidth + margin), "top":header + 3*(topicHeight + margin)};
	twentytopiclayout[19] = {"left":left + 4*(topicWidth + margin), "top":header + 3*(topicHeight + margin)};

	exports['twentytopiclayout'] = twentytopiclayout;
})(this);
