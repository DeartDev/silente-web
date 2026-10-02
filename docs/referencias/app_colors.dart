import 'package:flutter/painting.dart';

/// Silente colour tokens.
///
/// Brand tokens come from spec §6 unchanged. Derived "ink" tokens exist
/// because some spec colours do not reach WCAG AA as *text* on the light
/// surfaces (e.g. pageGold on parchmentWhite is 2.0:1); they are only used
/// where the spec colour would be unreadable (see docs/funcionalidades/design-system.md).
abstract final class AppColors {
  // Dark theme — base (spec §6.1).
  static const nightBlack = Color(0xFF121014);
  static const shadowGraphite = Color(0xFF1C1A22);
  static const ivoryMist = Color(0xFFEDEBE6);
  static const ashGray = Color(0xFFA6A3AA);
  static const pageGold = Color(0xFFC8A86B);
  static const deepOlive = Color(0xFF3A3F2C);

  // Light theme (spec §6.2).
  static const parchmentWhite = Color(0xFFF5F3EF);
  static const softLinen = Color(0xFFECEAE4);
  static const inkBlack = Color(0xFF1C1A22);
  static const warmGray = Color(0xFF6E6B73);
  static const mutedOlive = Color(0xFF7A7F66);

  // Brand-only (logo gradient; decorative, never text).
  static const duskLavender = Color(0xFF8C7FB8);

  // Derived accessibility tokens (light theme text).
  static const goldInk = Color(0xFF7D6128); // 5.2:1 on parchmentWhite
  static const warmGrayInk = Color(
    0xFF65626A,
  ); // ≥ 5.0:1 on parchment/softLinen
  static const oliveInk = Color(0xFF5E6349); // 5.6:1 on parchmentWhite

  // Errors (not in the spec palette; warm, calm tones).
  static const errorOnDark = Color(0xFFE5897A);
  static const errorOnLight = Color(0xFFA23B2E);
}
