import type { ComboboxOnChange } from '@invoke-ai/ui-library';
import { Combobox, FormControl, FormLabel } from '@invoke-ai/ui-library';
import { isLogLevel, zLogLevel } from 'app/logging/logger';
import { useAppDispatch, useAppSelector } from 'app/store/storeHooks';
import { logLevelChanged } from 'features/system/store/systemSlice';
import { memo, useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

export const SettingsLogLevelSelect = memo(() => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const logLevel = useAppSelector((s) => s.system.logLevel);
  const logIsEnabled = useAppSelector((s) => s.system.logIsEnabled);
  const options = useMemo(() => zLogLevel.options.map((o) => ({ label: o, value: o })), []);

  const value = useMemo(() => options.find((o) => o.value === logLevel), [logLevel, options]);

  const onChange = useCallback<ComboboxOnChange>(
    (v) => {
      if (!isLogLevel(v?.value)) {
        return;
      }
      dispatch(logLevelChanged(v.value));
    },
    [dispatch]
  );
  return (
    <FormControl isDisabled={!logIsEnabled}>
      <FormLabel>{t('common.loglevel')}</FormLabel>
      <Combobox value={value} options={options} onChange={onChange} />
    </FormControl>
  );
});

SettingsLogLevelSelect.displayName = 'SettingsLogLevelSelect';
