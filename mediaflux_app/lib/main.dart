import 'dart:io';
import 'dart:convert';
import 'package:before_after/before_after.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path/path.dart' as path;
import 'package:gal/gal.dart';
import 'services/api_service.dart';
import 'utils/constants.dart';
import 'package:flutter/foundation.dart';
import 'widgets/result_card.dart';

void main() {
  runApp(const MediaFluxApp());
}

class MediaFluxApp extends StatelessWidget {
  const MediaFluxApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'MediaFlux',
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF090B13),
        useMaterial3: true,
      ),
      home: const DashboardPage(),
    );
  }
}

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  double quality = 85;

  bool autoMode = false;

  bool isProcessing = false;

  bool isUploading = false;

  bool targetSizeEnabled = false;

  double targetSizeKb = 200;

  bool resizeEnabled = false;

  double resizeWidth = 1080;

  double resizeHeight = 1080;

  String currentJobId = "";

  double processingProgress = 0;

  String processingStage = "";

  String selectedFormat = 'WEBP';

  final ScrollController scrollController = ScrollController();

  int previousResultsCount = 0;

  final List<String> formats = ['WEBP', 'AVIF', 'PNG', 'JPEG'];

  List<XFile> uploadedFiles = [];

  List<dynamic> optimizationResults = [];

  Future<void> pickImages() async {
    final ImagePicker picker = ImagePicker();

    final List<XFile> images = await picker.pickMultiImage();

    if (images.isNotEmpty) {
      setState(() {
        uploadedFiles = images;
      });
    }
  }

  Future<void> downloadFile(String url, String filename) async {
    try {
      final tempDir = await getTemporaryDirectory();

      final tempPath = "${tempDir.path}/$filename";

      Dio dio = Dio();

      await dio.download(url, tempPath);

      await Gal.putImage(tempPath);

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Saved to Gallery / Downloads")),
      );
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Download failed: $e")));
    }
  }

  Future<void> uploadImages() async {
    if (uploadedFiles.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Select images first")));

      return;
    }

    setState(() {
      isUploading = true;

      isProcessing = true;

      processingProgress = 0;

      optimizationResults = [];

      previousResultsCount = 0;

      processingStage = "Uploading ${uploadedFiles.length} images...";
    });

    try {
      final uploadResponse = await ApiService.uploadImages(
        files: uploadedFiles,

        format: selectedFormat,

        quality: quality.toInt(),

        autoMode: autoMode,

        targetSizeEnabled: targetSizeEnabled,

        targetSizeKb: targetSizeKb.toInt(),

        resizeEnabled: resizeEnabled,

        resizeWidth: resizeWidth.toInt(),

        resizeHeight: resizeHeight.toInt(),
      );

      final String jobId = uploadResponse["job_id"];

      currentJobId = jobId;

      bool completed = false;

      while (!completed) {
        await Future.delayed(const Duration(seconds: 1));

        final jobResponse = await ApiService.getJobStatus(jobId);

        final job = jobResponse["job"];

        final status = job["status"];

        final updatedResults = List<dynamic>.from(job["results"] ?? []);

        final hasNewResult = updatedResults.length > previousResultsCount;

        setState(() {
          processingProgress = (job["progress"] ?? 0).toDouble();

          processingStage = job["current_stage"] ?? "Optimizing media...";

          optimizationResults = updatedResults;
        });

        if (hasNewResult) {
          previousResultsCount = updatedResults.length;

          if (hasNewResult) {
            previousResultsCount = updatedResults.length;

            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (scrollController.hasClients) {
                scrollController.animateTo(
                  scrollController.position.maxScrollExtent,

                  duration: const Duration(milliseconds: 800),

                  curve: Curves.easeOutCubic,
                );
              }
            });
          }

          if (scrollController.hasClients) {
            scrollController.animateTo(
              scrollController.position.maxScrollExtent,

              duration: const Duration(milliseconds: 700),

              curve: Curves.easeOutCubic,
            );
          }
        }

        if (status == "completed") {
          setState(() {
            isProcessing = false;

            isUploading = false;

            processingProgress = 100;
          });

          completed = true;
        }

        if (status == "failed") {
          setState(() {
            isProcessing = false;

            isUploading = false;
          });

          completed = true;

          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text("Processing failed")));
        }
      }
    } catch (e) {
      setState(() {
        isProcessing = false;

        isUploading = false;
      });

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;

    final isMobile = width < 900;

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          controller: scrollController,

          padding: const EdgeInsets.all(20),

          child: isMobile
              ? Column(
                  children: [
                    buildHeader(true),

                    const SizedBox(height: 24),

                    buildUploadSection(),

                    const SizedBox(height: 24),

                    buildSettingsPanel(),

                    const SizedBox(height: 24),

                    buildImagesSection(),

                    const SizedBox(height: 24),

                    buildResultsSection(),
                  ],
                )
              : Column(
                  children: [
                    buildHeader(false),

                    const SizedBox(height: 30),

                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,

                      children: [
                        Expanded(
                          flex: 3,

                          child: Column(
                            children: [
                              buildUploadSection(),

                              const SizedBox(height: 24),

                              buildImagesSection(),

                              const SizedBox(height: 24),

                              buildResultsSection(),
                            ],
                          ),
                        ),

                        const SizedBox(width: 24),

                        SizedBox(width: 350, child: buildSettingsPanel()),
                      ],
                    ),
                  ],
                ),
        ),
      ),
    );
  }

  Widget buildHeader(bool isMobile) {
    return Row(
      children: [
        Container(
          height: isMobile ? 70 : 90,

          width: isMobile ? 70 : 90,

          decoration: BoxDecoration(borderRadius: BorderRadius.circular(22)),

          child: ClipRRect(
            borderRadius: BorderRadius.circular(22),

            child: Image.asset('assets/logo.png', fit: BoxFit.cover),
          ),
        ),

        const SizedBox(width: 16),

        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,

            children: [
              Text(
                'MediaFlux',

                style: TextStyle(
                  fontSize: isMobile ? 32 : 42,

                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 4),

              Text(
                'Adaptive Media Optimization Engine',

                style: TextStyle(
                  color: Colors.white60,

                  fontSize: isMobile ? 12 : 16,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget buildUploadSection() {
    return InkWell(
      onTap: pickImages,

      borderRadius: BorderRadius.circular(30),

      child: Container(
        width: double.infinity,

        height: 320,

        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(30),

          gradient: const LinearGradient(
            colors: [Color(0xFF111423), Color(0xFF171A2B)],
          ),

          border: Border.all(color: Colors.white10, width: 2),
        ),

        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,

          children: [
            Container(
              padding: const EdgeInsets.all(22),

              decoration: BoxDecoration(
                color: Colors.deepPurple.withOpacity(0.15),

                shape: BoxShape.circle,
              ),

              child: const Icon(
                Icons.cloud_upload_rounded,

                size: 70,

                color: Colors.deepPurpleAccent,
              ),
            ),

            const SizedBox(height: 24),

            const Text(
              'Upload Images',

              style: TextStyle(fontSize: 34, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 10),

            Text(
              uploadedFiles.isEmpty
                  ? 'PNG, JPG, WEBP, AVIF supported'
                  : '${uploadedFiles.length} images selected',

              style: const TextStyle(color: Colors.white60, fontSize: 15),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildImagesSection() {
    return Container(
      width: double.infinity,

      padding: const EdgeInsets.all(22),

      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(30),

        color: const Color(0xFF121521),
      ),

      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,

        children: [
          const Text(
            'Uploaded Images',

            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),

          const SizedBox(height: 24),

          uploadedFiles.isEmpty
              ? const SizedBox(
                  height: 120,
                  child: Center(child: Text('No images uploaded yet')),
                )
              : GridView.builder(
                  shrinkWrap: true,

                  physics: const NeverScrollableScrollPhysics(),

                  itemCount: uploadedFiles.length,

                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: MediaQuery.of(context).size.width < 700
                        ? 1
                        : 2,

                    crossAxisSpacing: 20,

                    mainAxisSpacing: 20,

                    childAspectRatio: 1.3,
                  ),

                  itemBuilder: (context, index) {
                    final file = uploadedFiles[index];

                    return Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(22),

                        color: const Color(0xFF0B0D16),
                      ),

                      child: Column(
                        children: [
                          Expanded(
                            child: ClipRRect(
                              borderRadius: const BorderRadius.vertical(
                                top: Radius.circular(22),
                              ),

                              child: Image.file(
                                File(file.path),

                                width: double.infinity,

                                fit: BoxFit.cover,

                                errorBuilder: (context, error, stackTrace) {
                                  return Container(
                                    color: const Color(0xFF0B0D16),

                                    child: const Center(
                                      child: Icon(
                                        Icons.broken_image_rounded,

                                        color: Colors.redAccent,

                                        size: 50,
                                      ),
                                    ),
                                  );
                                },
                              ),
                            ),
                          ),

                          Padding(
                            padding: const EdgeInsets.all(12),

                            child: Text(
                              file.name,

                              maxLines: 1,

                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
        ],
      ),
    );
  }

  Widget buildResultsSection() {
    if (optimizationResults.isEmpty) {
      return const SizedBox();
    }

    double totalOriginalSize = 0;

    double totalOptimizedSize = 0;

    double averageCompression = 0;

    int minimalOptimizationCount = 0;

    for (var result in optimizationResults) {
      totalOriginalSize += result["original_size_kb"] ?? 0;

      totalOptimizedSize += result["optimized_size_kb"] ?? 0;

      averageCompression += result["saved_percent"] ?? 0;

      if ((result["saved_percent"] ?? 0) < 5) {
        minimalOptimizationCount++;
      }
    }

    final totalSaved = totalOriginalSize - totalOptimizedSize;

    if (optimizationResults.isNotEmpty) {
      averageCompression = averageCompression / optimizationResults.length;
    }

    return Container(
      margin: const EdgeInsets.only(top: 24),

      padding: const EdgeInsets.all(20),

      decoration: BoxDecoration(
        color: const Color(0xFF11152A),

        borderRadius: BorderRadius.circular(28),

        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),

      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,

        children: [
          const Text(
            "Optimization Results",

            style: TextStyle(
              color: Colors.white,

              fontSize: 30,

              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 24),

          Container(
            width: double.infinity,

            padding: const EdgeInsets.all(22),

            margin: const EdgeInsets.only(bottom: 28),

            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(24),

              gradient: LinearGradient(
                colors: [
                  Colors.deepPurple.withOpacity(0.25),

                  Colors.deepPurpleAccent.withOpacity(0.08),
                ],
              ),

              border: Border.all(color: Colors.deepPurple.withOpacity(0.2)),
            ),

            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,

              children: [
                const Text(
                  "Batch Summary",

                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),

                const SizedBox(height: 18),

                Row(
                  children: [
                    Expanded(
                      child: buildMiniInfo(
                        "Images",

                        optimizationResults.length.toString(),
                      ),
                    ),

                    const SizedBox(width: 14),

                    Expanded(
                      child: buildMiniInfo(
                        "Saved",

                        "${totalSaved.toStringAsFixed(1)} KB",
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 14),

                Row(
                  children: [
                    Expanded(
                      child: buildMiniInfo(
                        "Avg Compression",

                        "${averageCompression.toStringAsFixed(1)}%",
                      ),
                    ),

                    const SizedBox(width: 14),

                    Expanded(
                      child: buildMiniInfo(
                        "Quality Protected",

                        minimalOptimizationCount.toString(),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 20),

                Text(
                  minimalOptimizationCount > 0
                      ? "$minimalOptimizationCount images required only minimal optimization to preserve visual quality."
                      : "All images optimized successfully with strong compression efficiency.",

                  style: const TextStyle(color: Colors.white70, fontSize: 15),
                ),
              ],
            ),
          ),

          Column(
            children: List.generate(optimizationResults.length, (index) {
              final result = optimizationResults[index];

              return Padding(
                padding: const EdgeInsets.only(bottom: 24),

                child: ResultCard(
                  result: result,

                  baseUrl: AppConstants.baseUrl,

                  onDownload: () async {
                    await downloadFile(
                      "${AppConstants.baseUrl}/${result["optimized_file"]}",

                      result["filename"],
                    );

                    if (!mounted) return;

                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("Saved to Gallery / Downloads"),
                      ),
                    );
                  },
                ),
              );
            }),
          ),
        ],
      ),
    );
  }

  Widget buildMiniInfo(String title, String value) {
    return Container(
      padding: const EdgeInsets.all(16),

      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),

        color: const Color(0xFF151826),
      ),

      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,

        children: [
          Text(title, style: const TextStyle(color: Colors.white60)),

          const SizedBox(height: 8),

          Text(
            value,

            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
          ),
        ],
      ),
    );
  }

  Widget buildResultRow(String title, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),

      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,

        children: [
          Text(title, style: const TextStyle(color: Colors.white70)),

          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget buildSettingsPanel() {
    return Container(
      padding: const EdgeInsets.all(26),

      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(30),

        color: const Color(0xFF121521),
      ),

      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,

        children: [
          const Text(
            'Optimization Settings',

            style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
          ),

          const SizedBox(height: 34),

          // =========================
          // OUTPUT FORMAT
          // =========================
          const Text('Output Format'),

          const SizedBox(height: 14),

          DropdownButtonFormField<String>(
            value: selectedFormat,

            dropdownColor: const Color(0xFF121521),

            decoration: InputDecoration(
              filled: true,

              fillColor: const Color(0xFF0B0D16),

              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(18),
              ),
            ),

            items: formats.map((format) {
              return DropdownMenuItem(value: format, child: Text(format));
            }).toList(),

            onChanged: (value) {
              setState(() {
                selectedFormat = value!;
              });
            },
          ),

          const SizedBox(height: 30),

          // =========================
          // QUALITY
          // =========================
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,

            children: [const Text('Quality'), Text(quality.toInt().toString())],
          ),

          Slider(
            value: quality,

            min: 1,

            max: 100,

            divisions: 99,

            activeColor: Colors.deepPurpleAccent,

            onChanged: (value) {
              setState(() {
                quality = value;
              });
            },
          ),

          const SizedBox(height: 24),

          // =========================
          // AUTO MODE
          // =========================
          SwitchListTile(
            contentPadding: EdgeInsets.zero,

            title: const Text('Auto Mode'),

            subtitle: const Text('AI chooses best format'),

            value: autoMode,

            activeColor: Colors.deepPurple,

            onChanged: (value) {
              setState(() {
                autoMode = value;
              });
            },
          ),

          const SizedBox(height: 24),

          // =========================
          // TARGET SIZE
          // =========================
          SwitchListTile(
            contentPadding: EdgeInsets.zero,

            title: const Text('Target Size'),

            subtitle: Text('${targetSizeKb.toInt()} KB'),

            value: targetSizeEnabled,

            activeColor: Colors.deepPurple,

            onChanged: (value) {
              setState(() {
                targetSizeEnabled = value;
              });
            },
          ),

          if (targetSizeEnabled)
            Column(
              children: [
                Slider(
                  value: targetSizeKb,

                  min: 10,

                  max: 1000,

                  divisions: 99,

                  activeColor: Colors.deepPurpleAccent,

                  onChanged: (value) {
                    setState(() {
                      targetSizeKb = value;
                    });
                  },
                ),
              ],
            ),

          const SizedBox(height: 24),

          // =========================
          // RESIZE
          // =========================
          SwitchListTile(
            contentPadding: EdgeInsets.zero,

            title: const Text('Resize Image'),

            subtitle: Text('${resizeWidth.toInt()} x ${resizeHeight.toInt()}'),

            value: resizeEnabled,

            activeColor: Colors.deepPurple,

            onChanged: (value) {
              setState(() {
                resizeEnabled = value;
              });
            },
          ),

          if (resizeEnabled)
            Column(
              children: [
                const SizedBox(height: 10),

                Row(
                  children: [
                    Expanded(
                      child: Column(
                        children: [
                          const Text('Width'),

                          Slider(
                            value: resizeWidth,

                            min: 100,

                            max: 4000,

                            divisions: 39,

                            activeColor: Colors.deepPurpleAccent,

                            onChanged: (value) {
                              setState(() {
                                resizeWidth = value;
                              });
                            },
                          ),
                        ],
                      ),
                    ),

                    Expanded(
                      child: Column(
                        children: [
                          const Text('Height'),

                          Slider(
                            value: resizeHeight,

                            min: 100,

                            max: 4000,

                            divisions: 39,

                            activeColor: Colors.deepPurpleAccent,

                            onChanged: (value) {
                              setState(() {
                                resizeHeight = value;
                              });
                            },
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),

          const SizedBox(height: 40),

          // =========================
          // PROCESSING PROGRESS
          // =========================
          if (isProcessing)
            Column(
              children: [
                LinearProgressIndicator(
                  value: processingProgress / 100,

                  minHeight: 10,

                  borderRadius: BorderRadius.circular(12),

                  backgroundColor: Colors.black26,

                  color: Colors.deepPurpleAccent,
                ),

                const SizedBox(height: 10),

                Text(
                  "${processingProgress.toInt()}% • "
                  "${optimizationResults.length}/${uploadedFiles.length} completed",

                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),

                const SizedBox(height: 8),

                Text(
                  processingStage,

                  style: const TextStyle(color: Colors.white70, fontSize: 14),
                ),

                const SizedBox(height: 20),
              ],
            ),

          // =========================
          // BUTTON
          // =========================
          SizedBox(
            width: double.infinity,

            height: 65,

            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.deepPurple,

                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(22),
                ),
              ),

              onPressed: isUploading ? null : uploadImages,

              icon: isUploading
                  ? const SizedBox(
                      height: 22,

                      width: 22,

                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.auto_fix_high),

              label: Text(
                isUploading
                    ? '${processingProgress.toInt()}% Processing'
                    : 'Optimize Media',

                style: const TextStyle(
                  fontSize: 20,

                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
