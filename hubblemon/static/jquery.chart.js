
(function($){
	$.fn.donutChart = function(options) {
		
		var graphs = [];
		
		this.each(function(idx, table){
			graphs.push(createDonutChart(table));
		});
		
		return $(graphs);	
			
		function drawDonutChart(context, graph, items){

			var sum = items.reduce(function(prev, cur){return prev + cur.value;}, 0);
			var currentAngle = -1 * (Math.PI * 2 / 6);
			var length = Math.min(graph.width, graph.height);
			var centerX = Math.floor(graph.x + length / 2);
			var centerY = Math.floor(graph.y + length / 2) * (graph.label?1.1:1);
			var radius = Math.floor((length / 2) * 0.5);		
			
			items.sort(function(prev,curr){return prev.sortOrder - curr.sortOrder;});

			drawBorder(context, graph);
			
			drawGrapLabel(context, graph);
			
			drawGraphShadow(context, centerX + 5, centerY + 5, radius);
									
			// DRAW SEGMENTS
			for(var idx in items){
				var item = items[idx];
				var newAngle = (2 * Math.PI) * (item.value / sum);
						
				drawGraphSegment(context, centerX, centerY, radius, currentAngle, currentAngle + newAngle, item.color || "#" + (idx +"d").repeat(3));

				if(graph.legendBox.isLeft){
					drawLegendEntry(context, item, centerX + (length/2), (centerY - (graph.legendSize * 1.25 * items.length)/2) + (graph.legendSize * idx * 1.25), graph.legendSize, sum);
				}else{
					drawLegendEntry(context, item, graph.x + graph.legendSize, graph.y + graph.height - graph.legendSize/2 + (graph.legendSize * 1.25 * idx), graph.legendSize, sum);
				}

				currentAngle += newAngle;
			}
			
		}
		
		function drawBorder(context, graph){
			if(graph.hasBorder){
				context.beginPath();
				context.strokeStyle = "black";
				context.lineWidth = 1;	
				context.strokeRect(0, 0, graph.width + (graph.legendBox.isLeft ? graph.legendBox.width : 0), graph.height + (graph.legendBox.isLeft ? 0 : graph.legendBox.height));
				context.stroke();
			}
		}
		
		function drawGrapLabel(context, graph){
			if(graph.label){
				context.beginPath();
				context.strokeRect(0, 0, context.measureText(graph.label).width * 1.2, graph.legendSize * 1.25);
				context.stroke();
				
				context.font = "bold " + graph.legendSize + "px Arial ";
				context.textAlign = "left";
				context.fillStyle = "black";
				context.fillText(graph.label, (graph.x + graph.legendSize)  * 0.3 , graph.y + graph.legendSize );
			}
		}
		
		function drawLegendEntry(context, entry, x, y, size, sum){
			context.beginPath();
			context.fillStyle = entry.color;
			context.fillRect(x, y, size, size);
			context.stroke();
		
			context.font = "bold " + size + "px Arial ";
			context.textAlign = "left";
			context.fillStyle = entry.color;
			context.fillText(entry.description+" ("+parseInt(entry.value*100/sum)+"%)", x + (size * 1.5), y + size - 2 );
		}
	   
		function drawGraphShadow(context, x, y, radius, color){
			context.beginPath();
			context.strokeStyle = color || "#cfcfcf";
			context.lineWidth = radius;
			context.arc(x, y, radius, 0, Math.PI * 2, false);			
			context.stroke();
		}
	   
		function drawGraphSegment(context, x, y, radius, startAngle, drawAngle, color){
			context.beginPath();
			context.strokeStyle = color || "#" + (idx +"d").repeat(3);
			context.arc(x, y, radius, startAngle, drawAngle, false);
			context.stroke();
		}
  
		function positiveOrZero(value){
			return value < 0 ? 0 : value;
		}
		
		function createDonutChart(table){
			var items = [],
				graph = {x:0, y:0},
				opts = $.extend({}, $.fn.donutChart.defaults, options),
				legendSize = opts.legendSize || opts.height * opts.legendSizePadding,
				maxTextLength = items.reduce(function(prev,curr){
					return prev < curr.description.length ? curr.description.length : prev;
				}, 0),
				canvas = document.createElement("canvas"),
				context = canvas.getContext("2d");
				
			$(table).replaceWith(canvas);
			canvas.width = opts.width;
			canvas.height = opts.height;	
			
			$(table).find("tr:has(td)").each(function(idx, item){
				var data = item.innerHTML.match(/([^>]+)(?=<\/td>)/gi);
				items.push({sortOrder:data[0]*1, value:data[1]*1, color:data[2], description:data[3]});
			});
			
			graph.label = opts.label.replace(/{\d+}/, ++$.fn.donutChart.counter);
			
			graph.hasBorder = opts.hasBorder;
			
			graph.legendBox = {
				width : legendSize * maxTextLength ,
				height : legendSize * 1.25 * items.length 
			};	
			graph.legendBox.isLeft = (opts.width - graph.legendBox.width) > (opts.height - graph.legendBox.height);
	
			graph.width = !graph.legendBox.isLeft ? opts.width : positiveOrZero(opts.width - graph.legendBox.width);
			graph.height = graph.legendBox.isLeft ? opts.height : positiveOrZero(opts.height - graph.legendBox.height);
			graph.legendSize = legendSize;	

			drawDonutChart(context, graph, items);

			return $(canvas);
		}
		
	};
	
	$.fn.donutChart.counter = 0;
	
	$.fn.donutChart.defaults = {
		width: 600,
		height: 400,
		legendSizePadding: 0.05,
		label: "Graph {0}", 
		hasBorder: true
	};
		
})(jQuery);
