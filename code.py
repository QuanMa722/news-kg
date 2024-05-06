# -*- coding: utf-8 -*-

from fake_useragent import UserAgent
from zhipuai import ZhipuAI
import webbrowser
import requests
import re


class LM:

    def __init__(self, user):
        self.user = user

    def get_resp(self):
        client = ZhipuAI(api_key="aa9640ab2f76d114a6890d1762b4d8f4.eyQHBU2QTnTX4tH9")  # 请填写您自己的APIKey
        response = client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "user", "content": self.user},
            ],
        )
        resp_answer = response.choices[0].message.content

        return resp_answer


class News:

    ua = UserAgent()
    headers = {
        'User-Agent': ua.random
    }

    def __init__(self, url):
        # the news url
        self.url = url

    def get_text(self):
        resp = requests.get(self.url, headers=self.headers)

        html_text = resp.content.decode()

        user = f"从下列html中提取完整的新闻文本{html_text}。"

        lm = LM(user)
        resp_answer = lm.get_resp()

        print("-" * 50)
        print(resp_answer)
        print("-" * 50)

        return resp_answer


class Kg:

    def __init__(self, news_text):
        self.news_text = news_text

    def get_news_json(self):

        test_json = """
            {"source": "湖北省","target": "暴雪冻雨","type": "遭遇","rela": "天气现象"},
            {"source": "武汉","target": "暴雪冻雨","type": "遭遇","rela": "天气现象"}
        """

        user = (f"你是一个知识图谱专家，"
                f"请你根据输入的新闻 {self.news_text} 概括出绘制知识图谱的节点和边，"
                f"并得到类似于以下的 JSON 结果，"
                f"只需返回 JSON 结果即可，不要除json以外的话。") + test_json

        lm = LM(user)
        news_json = lm.get_resp()

        pattern = r'\[(.*?)\]'
        match = re.search(pattern, news_json, re.DOTALL)

        news_json = match.group()

        # user = (f"已下是一个知识图谱的json数据{news_json}，"
        #         f"你需要对这些数据进行修整，"
        #         f"例如湖北换为湖北省之类的，"
        #         f"其中包含省份与城市之间可以新添数据使之连接起来，"
        #         f"尽可能使这些节点能连接起来，"
        #         f"修改后以json数据形式返回。")
        #
        # lm_modify = LM(user)
        # news_json = lm_modify.get_resp()
        # pattern = r'\[(.*?)\]'
        # match = re.search(pattern, news_json, re.DOTALL)
        #
        # news_json = match.group()

        print(news_json)

        self.generate_html(news_json)

    @staticmethod
    def generate_html(news_json):
        html_content = """
        <!DOCTYPE html>
        <meta charset="utf-8">
        <style>.link {  fill: none;  stroke: #666;  stroke-width: 1.5px;}#licensing {  fill: green;}.link.licensing {  stroke: green;}.link.resolved {  stroke-dasharray: 0,2 1;}circle {  fill: #ccc;  stroke: #333;  stroke-width: 1.5px;}text {  font: 12px Microsoft YaHei;  pointer-events: none;  text-shadow: 0 1px 0 #fff, 1px 0 0 #fff, 0 -1px 0 #fff, -1px 0 0 #fff;}.linetext {    font-size: 12px Microsoft YaHei;}</style>
        <body>
        <script src="https://d3js.org/d3.v3.min.js"></script>
        <script>

        var links =
    
        %s
        
        ;

        var nodes = {};

        links.forEach(function(link)
        {
          link.source = nodes[link.source] || (nodes[link.source] = {name: link.source});
          link.target = nodes[link.target] || (nodes[link.target] = {name: link.target});
        });

        var width = 1920, height = 1080;

        var force = d3.layout.force()
            .nodes(d3.values(nodes))
            .links(links)
            .size([width, height])
            .linkDistance(180)
            .charge(-1500)
            .on("tick", tick)
            .start();

        var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height);

        var marker=
            svg.append("marker")
            .attr("id", "resolved")
            .attr("markerUnits","userSpaceOnUse")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX",32)
            .attr("refY", -1)
            .attr("markerWidth", 12)
            .attr("markerHeight", 12)
            .attr("orient", "auto")
            .attr("stroke-width",2)
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr('fill','#000000');

        var edges_line = svg.selectAll(".edgepath")
            .data(force.links())
            .enter()
            .append("path")
            .attr({
                  'd': function(d) {return 'M '+d.source.x+' '+d.source.y+' L '+ d.target.x +' '+d.target.y},
                  'class':'edgepath',
                  'id':function(d,i) {return 'edgepath'+i;}})
            .style("stroke",function(d){
                 var lineColor;
                 lineColor="#B43232";
                 return lineColor;
             })
            .style("pointer-events", "none")
            .style("stroke-width",0.5)
            .attr("marker-end", "url(#resolved)" );

        var edges_text = svg.append("g").selectAll(".edgelabel")
        .data(force.links())
        .enter()
        .append("text")
        .style("pointer-events", "none")
        .attr({  'class':'edgelabel',
                       'id':function(d,i){return 'edgepath'+i;},
                       'dx':80,
                       'dy':0
                       });

        edges_text.append('textPath')
        .attr('xlink:href',function(d,i) {return '#edgepath'+i})
        .style("pointer-events", "none")
        .text(function(d){return d.rela;});

        var circle = svg.append("g").selectAll("circle")
            .data(force.nodes())
            .enter().append("circle")
            .style("fill",function(node){
                var color;
                var link=links[node.index];
                color="#ADD8E6";
                return color;
            })
            .style('stroke',function(node){
                var color;
                var link=links[node.index];
                color="#ADD8E6";
                return color;
            })
            .attr("r", 28)
            .on("click",function(node)
            {
                edges_line.style("stroke-width",function(line){
                    console.log(line);
                    if(line.source.name==node.name || line.target.name==node.name){
                        return 4;
                    }else{
                        return 0.5;
                    }
                });
            })
            .call(force.drag);

        var text = svg.append("g").selectAll("text")
            .data(force.nodes())
            .enter()
            .append("text")
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .style('fill',function(node){
                var color;
                var link=links[node.index];
                color="#061119";
                return color;
            }).attr('x',function(d){
                var re_en = /[a-zA-Z]+/g;
                if(d.name.match(re_en)){
                     d3.select(this).append('tspan')
                     .attr('x',0)
                     .attr('y',2)
                     .text(function(){return d.name;});
                }

                else if(d.name.length<=4){
                     d3.select(this).append('tspan')
                    .attr('x',0)
                    .attr('y',2)
                    .text(function(){return d.name;});
                }else{
                    var top=d.name.substring(0,4);
                    var bot=d.name.substring(4,d.name.length);

                    d3.select(this).text(function(){return '';});

                    d3.select(this).append('tspan')
                        .attr('x',0)
                        .attr('y',-7)
                        .text(function(){return top;});

                    d3.select(this).append('tspan')
                        .attr('x',0)
                        .attr('y',10)
                        .text(function(){return bot;});
                }
            });

        function tick() {
          circle.attr("transform", transform1);
          text.attr("transform", transform2);

          edges_line.attr('d', function(d) {
              var path='M '+d.source.x+' '+d.source.y+' L '+ d.target.x +' '+d.target.y;
              return path;
          });

          edges_text.attr('transform',function(d,i){
                if (d.target.x<d.source.x){
                    bbox = this.getBBox();
                    rx = bbox.x+bbox.width/2;
                    ry = bbox.y+bbox.height/2;
                    return 'rotate(180 '+rx+' '+ry+')';
                }
                else {
                    return 'rotate(0)';
                }
           });
        }

        function linkArc(d) {
          return 'M '+d.source.x+' '+d.source.y+' L '+ d.target.x +' '+d.target.y
        }

        function transform1(d) {
          return "translate(" + d.x + "," + d.y + ")";
        }
        function transform2(d) {
              return "translate(" + (d.x) + "," + d.y + ")";
        }

        </script>
        """ % news_json

        with open(file="output.html", mode="w", encoding="utf-8") as file:
            file.write(html_content)

        webbrowser.open("output.html")


if __name__ == '__main__':
    news_url = "https://new.qq.com/rain/a/20240208A08B1200"

    news = News(news_url)
    news_text = news.get_text()

    kg = Kg(news_text)
    kg.get_news_json()

    print("Done.")
