import {
  $shift,
  CompositeSlider,
  FormControl,
  FormLabel,
  IconButton,
  NumberInput,
  NumberInputField,
  Popover,
  PopoverAnchor,
  PopoverArrow,
  PopoverBody,
  PopoverContent,
  PopoverTrigger,
} from '@invoke-ai/ui-library';
import { useAppDispatch, useAppSelector } from 'app/store/storeHooks';
import { snapToNearest } from 'features/controlLayers/konva/util';
import { entityOpacityChanged } from 'features/controlLayers/store/canvasV2Slice';
import { selectEntity } from 'features/controlLayers/store/selectors';
import { isDrawableEntity } from 'features/controlLayers/store/types';
import { clamp, round } from 'lodash-es';
import type { KeyboardEvent } from 'react';
import { memo, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PiCaretDownBold } from 'react-icons/pi';

function formatPct(v: number | string) {
  if (isNaN(Number(v))) {
    return '';
  }

  return `${round(Number(v), 2).toLocaleString()}%`;
}

function mapSliderValueToOpacity(value: number) {
  return value / 100;
}

function mapOpacityToSliderValue(opacity: number) {
  return opacity * 100;
}

function formatSliderValue(value: number) {
  return String(value);
}

const marks = [
  mapOpacityToSliderValue(0),
  mapOpacityToSliderValue(0.25),
  mapOpacityToSliderValue(0.5),
  mapOpacityToSliderValue(0.75),
  mapOpacityToSliderValue(1),
];

const sliderDefaultValue = mapOpacityToSliderValue(100);

const snapCandidates = marks.slice(1, marks.length - 1);

export const CanvasEntityOpacity = memo(() => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const selectedEntityIdentifier = useAppSelector((s) => s.canvasV2.selectedEntityIdentifier);
  const opacity = useAppSelector((s) => {
    const selectedEntityIdentifier = s.canvasV2.selectedEntityIdentifier;
    if (!selectedEntityIdentifier) {
      return null;
    }
    const selectedEntity = selectEntity(s.canvasV2, selectedEntityIdentifier);
    if (!selectedEntity) {
      return null;
    }
    if (!isDrawableEntity(selectedEntity)) {
      return null;
    }
    return selectedEntity.opacity;
  });

  const [localOpacity, setLocalOpacity] = useState((opacity ?? 1) * 100);

  const onChangeSlider = useCallback(
    (opacity: number) => {
      if (!selectedEntityIdentifier) {
        return;
      }
      let snappedOpacity = opacity;
      // Do not snap if shift key is held
      if (!$shift.get()) {
        snappedOpacity = snapToNearest(opacity, snapCandidates, 2);
      }
      const mappedOpacity = mapSliderValueToOpacity(snappedOpacity);

      dispatch(entityOpacityChanged({ entityIdentifier: selectedEntityIdentifier, opacity: mappedOpacity }));
    },
    [dispatch, selectedEntityIdentifier]
  );

  const onBlur = useCallback(() => {
    if (!selectedEntityIdentifier) {
      return;
    }
    if (isNaN(Number(localOpacity))) {
      setLocalOpacity(100);
      return;
    }
    dispatch(
      entityOpacityChanged({ entityIdentifier: selectedEntityIdentifier, opacity: clamp(localOpacity / 100, 0, 1) })
    );
  }, [dispatch, localOpacity, selectedEntityIdentifier]);

  const onChangeNumberInput = useCallback((valueAsString: string, valueAsNumber: number) => {
    setLocalOpacity(valueAsNumber);
  }, []);

  const onKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        onBlur();
      }
    },
    [onBlur]
  );

  useEffect(() => {
    setLocalOpacity((opacity ?? 1) * 100);
  }, [opacity]);

  return (
    <Popover>
      <FormControl w="min-content" gap={2}>
        <FormLabel m={0}>{t('controlLayers.opacity')}</FormLabel>
        <PopoverAnchor>
          <NumberInput
            display="flex"
            alignItems="center"
            min={0}
            max={100}
            step={1}
            value={localOpacity}
            onChange={onChangeNumberInput}
            onBlur={onBlur}
            w="76px"
            format={formatPct}
            defaultValue={1}
            onKeyDown={onKeyDown}
            clampValueOnBlur={false}
          >
            <NumberInputField paddingInlineEnd={7} />
            <PopoverTrigger>
              <IconButton
                aria-label="open-slider"
                icon={<PiCaretDownBold />}
                size="sm"
                variant="link"
                position="absolute"
                insetInlineEnd={0}
                h="full"
              />
            </PopoverTrigger>
          </NumberInput>
        </PopoverAnchor>
      </FormControl>
      <PopoverContent w={200} pt={0} pb={2} px={4}>
        <PopoverArrow />
        <PopoverBody>
          <CompositeSlider
            min={0}
            max={100}
            value={localOpacity}
            onChange={onChangeSlider}
            defaultValue={sliderDefaultValue}
            marks={marks}
            formatValue={formatSliderValue}
            alwaysShowMarks
          />
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
});

CanvasEntityOpacity.displayName = 'CanvasEntityOpacity';