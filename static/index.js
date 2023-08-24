document.addEventListener('DOMContentLoaded', function() {

    // Various views
    document.querySelector('#home').addEventListener('click', () => load_index());
    document.querySelector('#model-1').addEventListener('click', () => load_model('1'));
    document.querySelector('#model-2').addEventListener('click', () => load_model('2'));

    // Default view
    load_index();
});

function load_index() {
    
    // Index view won't change, thus no need to load it.
    document.querySelector('#model-1-view').style.display = 'None';
    document.querySelector('#model-2-view').style.display = 'None';
    document.querySelector('#index-view').style.display = 'block';
}

function load_model(model) {
    // Calling API to return model's predictions
    fetch('/models/' + model)
    .then(response => response.json())
    .then(stocks => {

        const m1view = document.querySelector('#model-1-view');

        // Loop over each stock
        for (const stock in stocks) {

            // Loop over each stock graph and prediction date
            for (const day in stocks[stock]['preds']) {

                var layout = {
                    font: {
                        color: 'white'
                    },

                    title: {
                        text: `${stock}'s forecast on ${day}`,
                        font: {
                            family: 'Courier New, monospace',
                            color: 'white',
                        },
                    },

                    xaxis: {
                        title: {
                          text: 'Day',
                          font: {
                            family: 'Courier New, monospace',
                            size: 18,
                            color: 'white'
                          }
                        },
                    },

                    yaxis: {
                        title: {
                          text: 'Price (USD)',
                          font: {
                            family: 'Courier New, monospace',
                            size: 18,
                            color: 'white'
                          }
                        },
                    },

                    plot_bgcolor: 'black',
                    paper_bgcolor:"black",
                    autosize: false,
                    width: window.screen.width,
                    height: 500,
                };

                const chart = stocks[stock]['preds'][day]
                var days = [];
                var prices = []

                chart.forEach(price => {
                    days.push(price.day)
                    prices.push(price.price)
                });

                var graph = {
                    x: days,
                    y: prices,
                    type: 'scatter',
                    name: stock,
                };

                const data2 = [graph];

                const newdiv = document.createElement('div');
                newdiv.id = `${stock}-div`;
                newdiv.classList.add('stock-div')

                const newdivgraph = document.createElement('div');
                newdivgraph.id = `${stock}-graph-div`;
                newdivgraph.style.display = 'None';

                const newdivheader = document.createElement('h3');
                newdivheader.innerHTML = `${stock}`;
                newdivheader.classList.add('stock-title');
                newdivheader.addEventListener('click', () => load_graph(stock))

                newdiv.appendChild(newdivgraph);
                newdiv.appendChild(newdivheader);

                m1view.appendChild(newdiv);

                Plotly.newPlot(`${stock}-graph-div`, data2, layout);
            }
            
        }

        document.querySelector('#model-1-view').style.display = 'block';
        document.querySelector('#model-2-view').style.display = 'None';
        document.querySelector('#index-view').style.display = 'None';
    })
}

function load_graph(stock) {
    graphdiv = document.getElementById(`${stock}-graph-div`);
    if (graphdiv.style.display == 'none') {
        graphdiv.style.display = 'block';
    } else {
        graphdiv.style.display = 'None';
    }
}