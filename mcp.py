import mcp3008
import time


def light():
    adc = mcp3008.MCP3008()
    value = adc.read([mcp3008.CH0])[0]
    adc.close()
    return value


if __name__ == "__main__":
    try:

        while True:

            adc = mcp3008.MCP3008()
            print("0",adc.read([mcp3008.CH0]))
            #print("1",adc.read([mcp3008.CH1]))         # prints raw data [CH0]
            time.sleep( 0.5 )

    except Exception as e:

        print(str(e))
