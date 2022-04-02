# My Freqtrade Strategies <a href="https://github.com/cyberjunky/freqtrade-cyber-bots/blob/main/README.md#donate"><img src="https://img.shields.io/badge/Donate-PayPal-green.svg" height="40" align="right"></a> 


Started to code and learn more about freqtrade strategies, when they are a little bit successful or just different than the rest I upload them here. 

They are probably not suited for unattended production use, and below license/disclaimers are in place.

## Disclaimer
```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
> My code is [MIT Licensed](LICENSE), read it please.

> Always test your setup and settings with DRY RUNS first!
 
## See You Later (Alligator)

I got inspired by the Alligator Indicator and Fractals signals described by trader Bill Williams, so I wrote this simple strategy to learn more about them. 

It does fairly well with volatile pairs, so you are adviced to use a static pair list with most volatile pairs. 
Mentioned is that the Alligator doesn't like sideways moving markets. (*it needs some peaks to bite in I guess*) 

See the tools in my `freqtrade-cyber-bots` repo for a way to change the pairs reguarly.

Only tested overnight with USDT pairs. 

## Usage

Copy the strategy to your strategy folder, check the contents, and install the tapy package.
For now it was the only indicatior set which gave reasoable Alligator and Fractal data.
May change later.

```
pip3 install tapy
```

I also included a built-in graph which you can load using the 'From Strategy' button.

## TODO's:
- Add more signal guards.
- Optimize the Fractals to look more than the TradingView indicator.
- Hyperopt ROI


## Donate
If you enjoyed this project -and want to support further improvement and development- consider sending a small donation using the PayPal button or one of the Crypto Wallets below. :v:
<a href="https://www.paypal.me/cyberjunkynl/"><img src="https://img.shields.io/badge/Donate-PayPal-green.svg" height="40" align="right"></a>  

Wallets:

- USDT (TRC20): TEQPsmmWbmjTdbufxkJvkbiVHhmL6YWK6R
- USDT (ERC20): 0x73b41c3996315e921cb38d5d1bca13502bd72fe5

- BTC (BTC)   : 18igByUc1W2PVdP7Z6MFm2XeQMCtfVZJw4
- BTC (ERC20) : 0x73b41c3996315e921cb38d5d1bca13502bd72fe5


## Disclamer (Reminder)
```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
> My code is [MIT Licensed](LICENSE), read it please.

> Always test your settings with DRY RUNS first!
