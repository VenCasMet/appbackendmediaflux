import 'package:flutter/material.dart';
import '../screens/compare_screen.dart';
import 'package:flutter_animate/flutter_animate.dart';

class ResultCard extends StatelessWidget {
  final Map<String, dynamic> result;

  final String baseUrl;

  final VoidCallback onDownload;

  const ResultCard({
    super.key,

    required this.result,

    required this.baseUrl,

    required this.onDownload,
  });

  @override
  Widget build(BuildContext context) {
    final originalUrl = "$baseUrl/${result["original_file"]}";

    final optimizedUrl = "$baseUrl/${result["optimized_file"]}";

    String? heatmapUrl;

    if (result["heatmap"] != null) {
      heatmapUrl = "$baseUrl/${result["heatmap"]}";
    }

    return Container(
          margin: const EdgeInsets.only(bottom: 30),

          padding: const EdgeInsets.all(20),

          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(28),

            color: const Color(0xFF121521),

            border: Border.all(color: Colors.white10),
          ),

          child: Column(
            mainAxisSize: MainAxisSize.min,

            crossAxisAlignment: CrossAxisAlignment.start,

            children: [
              // =========================
              // HEADER
              // =========================
              Row(
                children: [
                  Container(
                    height: 65,

                    width: 65,

                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(18),

                      color: Colors.deepPurple.withOpacity(0.2),
                    ),

                    child: const Icon(
                      Icons.auto_fix_high,

                      color: Colors.deepPurpleAccent,

                      size: 32,
                    ),
                  ),

                  const SizedBox(width: 16),

                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,

                      children: [
                        Text(
                          result["filename"],

                          maxLines: 1,

                          overflow: TextOverflow.ellipsis,

                          style: const TextStyle(
                            fontSize: 22,

                            fontWeight: FontWeight.bold,
                          ),
                        ),

                        const SizedBox(height: 4),

                        Text(
                          "${result["format"]} • Final Quality ${result["quality"]}",

                          style: const TextStyle(
                            color: Colors.white70,

                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 26),

              // =========================
              // IMAGES
              // =========================
              Row(
                children: [
                  Expanded(
                    child: Column(
                      children: [
                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,

                              MaterialPageRoute(
                                builder: (_) => CompareScreen(
                                  originalUrl: originalUrl,

                                  optimizedUrl: optimizedUrl,
                                ),
                              ),
                            );
                          },

                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(18),

                            child: Image.network(
                              originalUrl,

                              height: 180,

                              fit: BoxFit.cover,
                            ),
                          ),
                        ),

                        const SizedBox(height: 10),

                        const Text(
                          "Original",

                          style: TextStyle(
                            fontWeight: FontWeight.bold,

                            fontSize: 18,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(width: 16),

                  Expanded(
                    child: Column(
                      children: [
                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,

                              MaterialPageRoute(
                                builder: (_) => CompareScreen(
                                  originalUrl: originalUrl,

                                  optimizedUrl: optimizedUrl,
                                ),
                              ),
                            );
                          },

                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(18),

                            child: Image.network(
                              optimizedUrl,

                              height: 180,

                              fit: BoxFit.cover,
                            ),
                          ),
                        ),

                        const SizedBox(height: 10),

                        const Text(
                          "Optimized",

                          style: TextStyle(
                            fontWeight: FontWeight.bold,

                            color: Colors.deepPurpleAccent,

                            fontSize: 18,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 28),

              // =========================
              // COMPRESSION
              // =========================
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,

                children: [
                  const Text(
                    "Compression Saved",
                    style: TextStyle(fontSize: 18),
                  ),

                  Text(
                    "${result["saved_percent"]}%",

                    style: const TextStyle(
                      fontSize: 22,

                      color: Colors.deepPurpleAccent,

                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              ClipRRect(
                borderRadius: BorderRadius.circular(20),

                child: LinearProgressIndicator(
                  value: (result["saved_percent"] ?? 0).toDouble() / 100,

                  minHeight: 10,

                  backgroundColor: Colors.white10,

                  color: Colors.deepPurpleAccent,
                ),
              ),

              const SizedBox(height: 28),

              // =========================
              // STATS
              // =========================
              Row(
                children: [
                  Expanded(
                    child: buildStatCard(
                      title: "Original",

                      value: "${result["original_size_kb"]} KB",

                      icon: Icons.image_outlined,
                    ),
                  ),

                  const SizedBox(width: 14),

                  Expanded(
                    child: buildStatCard(
                      title: "Optimized",

                      value: "${result["optimized_size_kb"]} KB",

                      icon: Icons.bolt,
                    ),
                  ),
                ],
              ),

              if (heatmapUrl != null)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,

                  children: [
                    const SizedBox(height: 24),

                    const Text(
                      "Quality Loss Heatmap",

                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),

                    const SizedBox(height: 14),

                    GestureDetector(
                      onTap: () {
                        showDialog(
                          context: context,

                          builder: (_) {
                            return Dialog(
                              backgroundColor: Colors.black,

                              insetPadding: const EdgeInsets.all(10),

                              child: InteractiveViewer(
                                child: Image.network(
                                  heatmapUrl!,
                                  fit: BoxFit.contain,
                                ),
                              ),
                            );
                          },
                        );
                      },

                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(20),

                        child: Image.network(
                          heatmapUrl!,
                          height: 220,

                          width: double.infinity,

                          fit: BoxFit.contain,
                        ),
                      ),
                    ),
                  ],
                ),

              const SizedBox(height: 18),

              // =========================
              // SPACE SAVED
              // =========================
              buildHighlightCard(
                title: "Space Saved",

                value: "${result["saved_percent"]}%",
              ),

              const SizedBox(height: 28),

              // =========================
              // DOWNLOAD
              // =========================
              SizedBox(
                width: double.infinity,

                height: 60,

                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.deepPurple,

                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                    ),
                  ),

                  onPressed: onDownload,

                  icon: const Icon(Icons.download),

                  label: const Text(
                    "Download",

                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            ],
          ),
        )
        .animate()
        .fadeIn(duration: 800.ms)
        .slideY(
          begin: 0.35,

          end: 0,

          duration: 800.ms,

          curve: Curves.easeOutCubic,
        )
        .scale(
          begin: const Offset(0.95, 0.95),

          end: const Offset(1, 1),

          duration: 800.ms,
        );
  }

  Widget buildStatCard({
    required String title,

    required String value,

    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 10),

      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),

        color: const Color(0xFF0B0D16),
      ),

      child: Column(
        mainAxisSize: MainAxisSize.min,

        children: [
          Icon(icon, color: Colors.deepPurpleAccent, size: 28),

          const SizedBox(height: 10),

          Text(
            title,

            style: const TextStyle(color: Colors.white70, fontSize: 16),
          ),

          const SizedBox(height: 8),

          FittedBox(
            fit: BoxFit.scaleDown,

            child: Text(
              value,

              maxLines: 1,

              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  Widget buildHighlightCard({required String title, required String value}) {
    return Container(
      width: double.infinity,

      padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 20),

      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),

        gradient: LinearGradient(
          colors: [
            Colors.deepPurple.withOpacity(0.4),

            Colors.deepPurpleAccent.withOpacity(0.15),
          ],
        ),
      ),

      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,

        children: [
          const Text("Space Saved", style: TextStyle(fontSize: 18)),

          Flexible(
            child: FittedBox(
              fit: BoxFit.scaleDown,

              child: Text(
                value,

                style: const TextStyle(
                  fontSize: 30,

                  fontWeight: FontWeight.bold,

                  color: Colors.deepPurpleAccent,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
