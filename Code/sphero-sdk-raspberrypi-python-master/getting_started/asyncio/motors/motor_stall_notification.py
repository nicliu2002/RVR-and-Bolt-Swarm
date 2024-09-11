import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import asyncio
from sphero_sdk import SpheroRvrAsync
from sphero_sdk import SerialAsyncDal
from sphero_sdk import RawMotorModesEnum


loop = asyncio.get_event_loop()

rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)


async def motor_stall_handler(response):
    print('Motor stall response:', response)


async def main():
    """ This program demonstrates how to receive motor stall notifications, in the event that RVR's treads become
        obstructed, and is unable to move.  In order to receive the notification, RVR's motors must be in use.
    """

    await rvr.wake()

    await rvr.enable_motor_stall_notify(is_enabled=True)

    await rvr.on_motor_stall_notify(handler=motor_stall_handler)

    # Give RVR time to wake up
    await asyncio.sleep(1)

    print('Press CTRL+C to stop this program anytime.')

    while True:
        await rvr.raw_motors(
            left_mode=RawMotorModesEnum.forward.value,
            left_duty_cycle=128,  # Valid duty cycle values are 0-255
            right_mode=RawMotorModesEnum.forward.value,
            right_duty_cycle=128  # Valid duty cycle values are 0-255
        )

        # Delay to allow RVR to drive
        await asyncio.sleep(1)


if __name__ == '__main__':
    try:
        loop.run_until_complete(
            main()
        )

    except KeyboardInterrupt:
        print('\nProgram terminated with keyboard interrupt.')

        loop.run_until_complete(
            rvr.close()
        )

    finally:
        if loop.is_running():
            loop.close()
